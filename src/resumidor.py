import logging
from functools import (
    lru_cache,  # armazenar em memória o resultado de uma função, evitando executar novamente operações que já foram realizadas.
)
from pathlib import Path

import pandas as pd
import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

BASE = Path(__file__).resolve().parent.parent

ARQUIVO = BASE / "data" / "raw" / "noticias.csv"

MODELO = "recogna-nlp/ptt5-base-summ-cstnews"

COLUNA_TEXTO = "texto"

MAX_TOKENS_ENTRADA = 512
MAX_TOKENS_RESUMO = 150

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def carregar_noticias():
    # Carrega as notícias uma única vez

    df = pd.read_csv(ARQUIVO)

    if COLUNA_TEXTO not in df.columns:
        raise ValueError(f"A coluna '{COLUNA_TEXTO}' não foi encontrada.")

    return df


@lru_cache(maxsize=1)
def carregar_modelo():
    # Carrega o modelo e o tokenizer uma única vez

    dispositivo = torch.device("cpu")

    tokenizer = AutoTokenizer.from_pretrained(MODELO)

    model = AutoModelForSeq2SeqLM.from_pretrained(
        MODELO,
        dtype=torch.float32,
    )

    model.to(dispositivo)
    model.eval()

    logger.info("Modelo de sumarização carregado.")

    return tokenizer, model, dispositivo


def resumir_noticia(manchete: str) -> str:
    # Recebe a manchete de uma notícia e retorna seu resumo.
    # Args:
    #     manchete: manchete da notícia que será resumida.
    # Returns:
    #     Resumo da notícia em formato de texto.

    df = carregar_noticias()

    noticia = df.loc[df["titulo"] == manchete]

    if noticia.empty:
        raise LookupError("Notícia não encontrada.")

    texto = noticia["texto"].iloc[0]

    if pd.isna(texto) or not str(texto).strip():
        raise ValueError("A notícia não possui texto válido.")

    tokenizer, model, dispositivo = carregar_modelo()

    entradas = tokenizer(
        str(texto),
        return_tensors="pt",
        truncation=True,
        max_length=MAX_TOKENS_ENTRADA,
    )

    entradas = {chave: valor.to(dispositivo) for chave, valor in entradas.items()}

    with torch.inference_mode():
        saida = model.generate(
            **entradas,
            max_new_tokens=MAX_TOKENS_RESUMO,
            num_beams=2,
            no_repeat_ngram_size=3,
            repetition_penalty=1.2,
            length_penalty=1.0,
            early_stopping=True,
            do_sample=False,
        )

    resumo = tokenizer.decode(
        saida[0],
        skip_special_tokens=True,
    )

    return resumo.strip()
