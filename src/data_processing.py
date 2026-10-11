import re
from pathlib import Path

import nltk
import pandas as pd
from unidecode import unidecode

BASE = Path(__file__).resolve().parent.parent
RAW = BASE / "data" / "raw"
PROCESSED = BASE / "data" / "processed"

arquivo = "noticias.csv"

df = pd.read_csv(RAW / arquivo, encoding="utf-8")
# print(df)

df["full_text"] = df["titulo"] + "\n" + df["texto"]
df["full_text"] = df["full_text"].str.lower().str.strip().apply(unidecode)
df["full_text"] = df["full_text"].str.replace(r"[^\w\s]", "", regex=True)


df = df.rename(columns={"titulo": "manchete"})
df["data"] = pd.to_datetime(df["data"], format="%d/%m/%Y - %H:%M")
df = df.sort_values(by="data", ascending=False)
texto = df["full_text"].copy()
df = df[["fonte", "manchete", "data", "palavras", "url"]]

df.to_csv(PROCESSED / arquivo, encoding="utf-8", index=False)
texto.to_csv(PROCESSED / "texto.csv", encoding="utf-8", index=False)


stopwords_raw = RAW / "stopwords_pt.txt"
stopwords_processed = PROCESSED / "stopwords_pt.txt"
custom_stopwords = ["us"]


if not stopwords_raw.exists():
    try:
        nltk.download("stopwords", quiet=True)
        stop_words = stopwords.words("portuguese")

        with open(stopwords_raw, "w", encoding="utf-8") as arquivo:
            arquivo.write("\n".join(stop_words))

    except Exception as erro:
        print(f"Não foi possível baixar as stopwords: {erro}")


if stopwords_raw.exists():

    with open(stopwords_raw, encoding="utf-8") as arquivo:
        stop_words = arquivo.read().splitlines()

    # Retirando acentos, uma vez que já foram retirados das notícias
    new_stopwords = []

    for word in stop_words:
        word = unidecode(word)

        if word not in new_stopwords:
            new_stopwords.append(word)

    for word in custom_stopwords:
        if word not in new_stopwords:
            new_stopwords.append(word)

    with open(stopwords_processed, "w", encoding="utf-8") as arquivo:
        arquivo.write("\n".join(new_stopwords))
