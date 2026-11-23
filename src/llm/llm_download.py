import argparse
import sys
import time
from pathlib import Path

from huggingface_hub import snapshot_download

MODELOS = [
    # "recogna-nlp/ptt5-base-summ-xlsum",
    "recogna-nlp/ptt5-base-summ-cstnews",
    # "csebuetnlp/mT5_multilingual_XLSum",
    # "openai-community/gpt2-large",
    # "Qwen/Qwen2.5-0.5B-Instruct",
    # "google/flan-t5-base",
]


def baixar_modelo(modelo: str, cache_dir: str | None = None) -> bool:
    print("\n" + "=" * 75)
    print(f"Modelo: {modelo}")
    print("=" * 75)

    inicio = time.perf_counter()

    try:
        caminho = snapshot_download(
            repo_id=modelo,
            cache_dir=cache_dir,
        )
        duracao = time.perf_counter() - inicio

        print(f"\nConcluído: {modelo}")
        print(f"Localização: {caminho}")
        print(f"Tempo: {duracao:.1f} segundos")
        return True

    except Exception as erro:
        print(f"\nERRO ao baixar {modelo}: {erro}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Baixa previamente os modelos de sumarização e comparação."
    )
    parser.add_argument(
        "--cache-dir",
        default=None,
        help=(
            "Diretório de cache opcional. Se omitido, usa o cache padrão "
            "do Hugging Face."
        ),
    )
    args = parser.parse_args()

    print("DOWNLOAD PRÉVIO DOS MODELOS")
    print(f"Quantidade de modelos: {len(MODELOS)}")
    print(
        "Cache: "
        + (
            str(Path(args.cache_dir).resolve())
            if args.cache_dir
            else "padrão do Hugging Face"
        )
    )
    print("\nOs modelos serão baixados um por vez.")

    concluidos = []
    falhas = []

    for modelo in MODELOS:
        if baixar_modelo(modelo, args.cache_dir):
            concluidos.append(modelo)
        else:
            falhas.append(modelo)

    print("\n" + "=" * 75)
    print("RESUMO")
    print("=" * 75)
    print(f"Concluídos: {len(concluidos)}/{len(MODELOS)}")

    if concluidos:
        print("\nModelos disponíveis:")
        for modelo in concluidos:
            print(f"  [OK] {modelo}")

    if falhas:
        print("\nModelos com falha:")
        for modelo in falhas:
            print(f"  [ERRO] {modelo}")
        print(
            "\nExecute o script novamente para tentar baixar os modelos que faltaram."
        )
        sys.exit(1)

    print("\nTodos os modelos estão disponíveis no cache.")


if __name__ == "__main__":
    main()
