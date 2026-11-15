import argparse
import gc
import os
import platform
import statistics
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
import torch
from huggingface_hub import snapshot_download
from transformers import AutoConfig, pipeline

BASE = Path(__file__).resolve().parent.parent.parent

CACHE = BASE / "data" / "raw" / "noticias.csv"
SAIDA = BASE / "src" / "llm" / "avaliacao_resumos.txt"

MAX_TOKENS_RESUMO = 250

MODELOS = {
    "recogna-nlp/ptt5-base-summ-xlsum": "summarization",
    "recogna-nlp/ptt5-base-summ-cstnews": "summarization",
    # "csebuetnlp/mT5_multilingual_XLSum": "summarization",
    # "openai-community/gpt2-large": "gpt2",
    # "Qwen/Qwen2.5-0.5B-Instruct": "qwen",
}


def carregar_noticias():
    """Carrega as notícias e mantém os índices originais."""

    df = pd.read_csv(CACHE)

    if "texto" not in df.columns:
        raise ValueError("O arquivo não possui a coluna 'texto'.")

    df = df.dropna(subset=["texto"]).copy()

    df["texto"] = df["texto"].astype(str).str.strip()
    df = df[df["texto"] != ""]

    if len(df) < 10:
        raise ValueError("São necessárias pelo menos 10 notícias válidas.")

    return df


def selecionar_noticias(df, seed):
    """Seleciona três notícias uma única vez para todos os modelos."""

    selecionadas = df.sample(n=10, random_state=seed)

    return [
        {
            "indice": indice,
            "texto": linha["texto"],
        }
        for indice, linha in selecionadas.iterrows()
    ]


def preparar_modelo(modelo, dtype):
    """Localiza os arquivos no cache e carrega o modelo."""

    tarefa = MODELOS[modelo]
    tipo = "auto" if dtype == "auto" else getattr(torch, dtype)

    inicio = time.perf_counter()

    caminho = snapshot_download(
        repo_id=modelo,
        local_files_only=True,
    )

    verificacao_cache = time.perf_counter() - inicio

    config = AutoConfig.from_pretrained(
        caminho,
        local_files_only=True,
    )

    inicio = time.perf_counter()

    if tarefa == "summarization":

        # Carregamento direto, sem o pipeline removido no Transformers 5.
        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

        tokenizer = AutoTokenizer.from_pretrained(
            caminho,
            local_files_only=True,
        )

        model = AutoModelForSeq2SeqLM.from_pretrained(
            caminho,
            dtype=tipo,
            local_files_only=True,
        )

        model.eval()

        pipe = {
            "model": model,
            "tokenizer": tokenizer,
        }

    else:

        pipe = pipeline(
            "text-generation",
            model=caminho,
            dtype=tipo,
            device="cpu",
        )

    carregamento = time.perf_counter() - inicio

    model = pipe["model"] if tarefa == "summarization" else pipe.model

    parametros = sum(p.numel() for p in model.parameters())

    pesos = sum(p.numel() * p.element_size() for p in model.parameters())

    detalhes = {
        "tarefa": tarefa,
        "arquitetura": (
            "encoder-decoder"
            if getattr(config, "is_encoder_decoder", False)
            else "decoder"
        ),
        "parametros": f"{parametros:,}".replace(",", "."),
        "dtype": str(next(model.parameters()).dtype).replace("torch.", ""),
        "pesos_mb": round(pesos / 1e6, 1),
        "verificacao_cache_s": round(verificacao_cache, 2),
        "carregamento_s": round(carregamento, 2),
    }

    return pipe, detalhes


def contar_tokens(tokenizer, texto):
    """Conta os tokens do texto."""

    return len(
        tokenizer(
            texto,
            truncation=True,
        )["input_ids"]
    )


def resumir(pipe, texto, tarefa):

    if tarefa == "summarization":

        model = pipe["model"]
        tokenizer = pipe["tokenizer"]

        entradas = tokenizer(
            texto,
            return_tensors="pt",
            truncation=True,
            max_length=512,
        )

        with torch.inference_mode():
            # saida = model.generate(
            #     **entradas,
            #     max_new_tokens=MAX_TOKENS_RESUMO,
            #     do_sample=False,
            # )
            saida = model.generate(
                **entradas,
                max_new_tokens=150,
                num_beams=4,
                repetition_penalty=1.2,
                no_repeat_ngram_size=3,
                length_penalty=1.0,
                early_stopping=True,
                do_sample=False,
            )

        resumo = tokenizer.decode(
            saida[0],
            skip_special_tokens=True,
        )

    elif tarefa == "gpt2":

        limite_contexto = 1024
        limite_entrada = limite_contexto - 150 - 10

        tokens = pipe.tokenizer.encode(texto, add_special_tokens=False)

        texto_cortado = pipe.tokenizer.decode(
            tokens[:limite_entrada], skip_special_tokens=True
        )

        prompt = "Texto:\n" f"{texto_cortado}\n\n" "Resumo:\n"

        resultado = pipe(
            prompt,
            max_new_tokens=150,
            do_sample=False,
            truncation=True,
            return_full_text=False,
            pad_token_id=pipe.tokenizer.eos_token_id,
        )

        resumo = resultado[0]["generated_text"]

    # elif tarefa == "gpt2":

    #     prompt = "Texto:\n" f"{texto}\n\n" "Resumo:\n"

    #     resultado = pipe(
    #         prompt,
    #         max_new_tokens=MAX_TOKENS_RESUMO,
    #         do_sample=False,
    #         truncation=True,
    #         return_full_text=False,
    #         pad_token_id=pipe.tokenizer.eos_token_id,
    #     )

    #     resumo = resultado[0]["generated_text"]

    elif tarefa == "qwen":

        mensagens = [
            {
                "role": "system",
                "content": (
                    "Você é um assistente especializado em resumir notícias "
                    "em português brasileiro. Faça um resumo completo e "
                    "coerente ao texto original, com máximo de "
                    "150 palavras. Não interrompa frases e não invente "
                    "informações. Responda com 'Resumo: '."
                ),
            },
            {
                "role": "user",
                "content": ("Resuma a seguinte notícia em português:\n\n" f"{texto}"),
            },
        ]

        prompt = pipe.tokenizer.apply_chat_template(
            mensagens,
            tokenize=False,
            add_generation_prompt=True,
        )

        resultado = pipe(
            prompt,
            max_new_tokens=MAX_TOKENS_RESUMO,
            do_sample=False,
            truncation=True,
            return_full_text=False,
            pad_token_id=pipe.tokenizer.eos_token_id,
        )

        resumo = resultado[0]["generated_text"]

    else:
        raise ValueError(f"Tarefa desconhecida: {tarefa}")

    return resumo.strip()


def avaliar_modelo(modelo, noticias, dtype):
    """Avalia um modelo nas três notícias selecionadas."""

    pipe, detalhes = preparar_modelo(modelo, dtype)

    tarefa = detalhes["tarefa"]
    tokenizer = pipe["tokenizer"] if tarefa == "summarization" else pipe.tokenizer

    # Aquecimento: não entra na medição.
    resumir(
        pipe,
        noticias[0]["texto"],
        tarefa,
    )

    resultados = []
    tempos = []

    for noticia in noticias:

        texto = noticia["texto"]

        inicio = time.perf_counter()

        resumo = resumir(
            pipe,
            texto,
            tarefa,
        )

        tempo = time.perf_counter() - inicio

        tokens_entrada = contar_tokens(
            tokenizer,
            texto,
        )

        tokens_saida = contar_tokens(
            tokenizer,
            resumo,
        )

        compressao = (1 - tokens_saida / tokens_entrada) * 100 if tokens_entrada else 0

        tempos.append(tempo)

        resultados.append(
            {
                "indice": noticia["indice"],
                "resumo": resumo,
                "tempo_s": round(tempo, 2),
                "tokens_entrada": tokens_entrada,
                "tokens_saida": tokens_saida,
                "compressao_pct": round(compressao, 1),
            }
        )

        print(f"  Notícia {noticia['indice']}: " f"{tempo:.2f} segundos")

    detalhes.update(
        {
            "tempo_medio_s": round(statistics.mean(tempos), 2),
            "tempo_mediano_s": round(statistics.median(tempos), 2),
            "tempo_max_s": round(max(tempos), 2),
            "resultados": resultados,
        }
    )

    return detalhes


def salvar_resultados(modelos, noticias, resultados, seed, dtype):
    """Salva as informações e os resumos em arquivo TXT."""

    SAIDA.parent.mkdir(parents=True, exist_ok=True)

    with open(SAIDA, "w", encoding="utf-8") as arquivo:

        arquivo.write("AVALIAÇÃO DE MODELOS DE SUMARIZAÇÃO\n")
        arquivo.write("=" * 75 + "\n")

        arquivo.write(f"Data: {datetime.now():%d/%m/%Y %H:%M:%S}\n")

        arquivo.write(f"Sistema: {platform.system()} {platform.release()}\n")

        arquivo.write(f"Processadores lógicos: {os.cpu_count()}\n")

        arquivo.write("Dispositivo: CPU\n")
        arquivo.write(f"Dtype solicitado: {dtype}\n")
        arquivo.write(f"Seed da seleção: {seed}\n")
        arquivo.write(f"Quantidade de notícias: {len(noticias)}\n")

        arquivo.write("\nNOTÍCIAS SELECIONADAS\n")
        arquivo.write("=" * 75 + "\n")

        for i, noticia in enumerate(noticias, start=1):

            arquivo.write(f"\nNotícia {i} | Índice original: {noticia['indice']}\n")

            arquivo.write("-" * 75 + "\n")
            arquivo.write(noticia["texto"] + "\n")

        for modelo, dados in resultados.items():

            arquivo.write("\n\n")
            arquivo.write("=" * 75 + "\n")
            arquivo.write(f"MODELO: {modelo}\n")
            arquivo.write("=" * 75 + "\n")

            if "erro" in dados:
                arquivo.write(f"\nERRO: {dados['erro']}\n")
                continue

            for chave, valor in dados.items():

                if chave != "resultados":
                    arquivo.write(f"{chave}: {valor}\n")

            for i, resultado in enumerate(
                dados["resultados"],
                start=1,
            ):

                arquivo.write(f"\nNotícia {i} | Índice: {resultado['indice']}\n")

                arquivo.write("-" * 75 + "\n")

                arquivo.write(f"Resumo:\n{resultado['resumo']}\n")

                arquivo.write(f"Tempo: {resultado['tempo_s']} segundos\n")

                arquivo.write(
                    f"Tokens: {resultado['tokens_entrada']} entrada / "
                    f"{resultado['tokens_saida']} saída\n"
                )

                arquivo.write(
                    f"Compressão aproximada: " f"{resultado['compressao_pct']}%\n"
                )

    print(f"\nResultados salvos em: {SAIDA}")


def main():

    parser = argparse.ArgumentParser(description="Avalia modelos de sumarização.")

    parser.add_argument(
        "modelos",
        nargs="*",
        help="IDs dos modelos no Hugging Face.",
    )

    parser.add_argument(
        "--dtype",
        choices=[
            "float32",
            "bfloat16",
            "float16",
            "auto",
        ],
        default="float32",
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=324234,
    )

    args = parser.parse_args()

    modelos = args.modelos if args.modelos else list(MODELOS.keys())

    # Valida os modelos informados.
    desconhecidos = [modelo for modelo in modelos if modelo not in MODELOS]

    if desconhecidos:
        raise ValueError(f"Modelos não cadastrados: {desconhecidos}")

    df = carregar_noticias()

    # Seleção realizada apenas uma vez.
    noticias = selecionar_noticias(
        df,
        args.seed,
    )

    resultados = {}

    for modelo in modelos:

        print(f"\nAvaliando: {modelo}")

        try:

            resultados[modelo] = avaliar_modelo(
                modelo,
                noticias,
                args.dtype,
            )

            dados = resultados[modelo]

            print(
                f"Mediana: {dados['tempo_mediano_s']} s | "
                f"Média: {dados['tempo_medio_s']} s | "
                f"Pesos: {dados['pesos_mb']} MB"
            )

        except Exception as erro:

            print(f"Erro ao avaliar {modelo}: {erro}")

            resultados[modelo] = {
                "erro": str(erro),
            }

        finally:
            gc.collect()

    salvar_resultados(
        modelos,
        noticias,
        resultados,
        args.seed,
        args.dtype,
    )


if __name__ == "__main__":
    main()
