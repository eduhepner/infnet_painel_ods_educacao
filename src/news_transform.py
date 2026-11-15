import io
import os
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import unidecode
from sklearn.feature_extraction.text import CountVectorizer
from wordcloud import WordCloud

BASE = Path(__file__).resolve().parent.parent
PROCESSED = BASE / "data" / "processed"
COLUNAS_OBRIGATORIAS = ["manchete", "url"]
ENVIADAS = BASE / "data" / "cache" / "noticias_enviadas.csv"
arquivo = "noticias.csv"


def load_news():
    df = pd.read_csv(PROCESSED / arquivo)
    texto = pd.read_csv(PROCESSED / "texto.csv")
    return df, texto


def filtro_news(df, opcoes):
    df = df[df["fonte"].isin(opcoes)]
    return df


def ordenar_news(df, opcoes):
    df["data"] = pd.to_datetime(df["data"], format="mixed", errors="coerce")
    if opcoes == "Mais recentes":
        df = df.sort_values(by="data", ascending=False)
    elif opcoes == "Mais antigas":
        df = df.sort_values(by="data", ascending=True)
    return df


def metrics_news(df):
    n_noticias = df.shape[0]
    n_fontes = df["fonte"].nunique()
    n_palavras = df["palavras"].sum()

    df["data"] = pd.to_datetime(df["data"])
    data_inicial = df["data"].min().date()
    data_final = df["data"].max().date()

    return n_noticias, n_fontes, n_palavras, data_inicial, data_final


def processar_news(col):
    with open(PROCESSED / "stopwords_pt.txt") as stopwords_pt:
        stop_words = stopwords_pt.read().splitlines()

    vectorizer = CountVectorizer(
        token_pattern=r"(?u)\b[A-Za-z][A-Za-z]+\b",  # pelo menos 2 letras
        stop_words=stop_words,
        strip_accents="unicode",
        ngram_range=(1, 1),
    )

    bag_of_words = vectorizer.fit_transform(col)

    contagens = bag_of_words.sum(axis=0)
    contagens = contagens.tolist()[0]

    tokens = vectorizer.get_feature_names_out()

    freqs = [(word, count) for word, count in zip(tokens, contagens)]
    freqs = sorted(freqs, key=lambda x: x[1], reverse=True)

    return freqs


def create_wordcloud(freqs):
    fig, ax = plt.subplots(figsize=(14, 7))

    wc = WordCloud(
        width=1200,
        height=600,
        background_color=None,
        mode="RGBA",
        max_words=100,
        min_font_size=8,
        max_font_size=140,
        prefer_horizontal=0.9,
    ).generate_from_frequencies(dict(freqs))

    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    fig.tight_layout()
    return fig


def ler_csv_enviado(conteudo: bytes) -> tuple[list[dict] | None, str | None]:

    if not conteudo:
        return None, "O arquivo está vazio."

    for codificacao in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            texto = conteudo.decode(codificacao)
            break
        except UnicodeDecodeError:
            continue
    else:
        return None, "Não consegui ler o arquivo como texto. Ele é mesmo um CSV?"

    try:
        df = pd.read_csv(io.StringIO(texto))
    except (pd.errors.ParserError, pd.errors.EmptyDataError):
        return None, "O arquivo não é um CSV válido."

    if df.empty:
        return None, "O CSV não tem nenhuma linha de dados."

    df.columns = df.columns.str.lower().str.strip()
    df = df.astype(object).where(pd.notna(df), None)

    return df.to_dict(orient="records"), None


def padronizar_texto_enviado(df):
    df["full_text"] = df["titulo"] + "\n" + df["texto"]
    df["full_text"] = df["full_text"].str.lower().str.strip().apply(unidecode)
    df["full_text"] = df["full_text"].str.replace(r"[^\w\s]", "", regex=True)
    pass


def salvar_news(df):
    colunas = ["fonte", "manchete", "data", "palavras", "url"]
    if not os.path.exists(ENVIADAS):
        df_base = pd.DataFrame(columns=colunas)
    else:
        df_base = pd.read_csv(ENVIADAS)
    df = df.reindex(columns=colunas)
    df_final = pd.concat([df_base, df], ignore_index=True)
    df_final = df_final.drop_duplicates(subset="url", keep="first")
    df_final.to_csv(ENVIADAS, index=False)
    # df.to_csv(ENVIADAS, mode="a", index=False, header=not ENVIADAS.exists())
