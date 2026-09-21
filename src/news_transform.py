import io
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import unidecode
from sklearn.feature_extraction.text import CountVectorizer
from wordcloud import WordCloud

BASE = Path(__file__).resolve().parent.parent
PROCESSED = BASE / "data" / "processed"
COLUNAS_OBRIGATORIAS = ["manchete", "url"]
arquivo = "noticias_19_09_2026.csv"


def load_news():
    df = pd.read_csv(PROCESSED / arquivo)
    texto = pd.read_csv(PROCESSED / "texto.csv")
    return df, texto


def filtro_news(df, opcoes):
    df = df[df["fonte"].isin(opcoes)]
    return df


def ordenar_news(df, opcoes):
    df["data"] = pd.to_datetime(df["data"])
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


def ler_csv_enviado(conteudo: bytes) -> tuple[list[dict], str]:

    if not conteudo:
        return [], "O arquivo está vazio."

    for codificacao in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            texto = conteudo.decode(codificacao)
            break
        except UnicodeDecodeError:
            continue
    else:
        return [], "Não consegui ler o arquivo como texto. Ele é mesmo um CSV?"

    try:
        df = pd.read_csv(io.StringIO(texto))
    except (pd.errors.ParserError, pd.errors.EmptyDataError):
        return [], "O arquivo não é um CSV válido."

    if df.empty:
        return [], "O CSV não tem nenhuma linha de dados."

    df.columns = df.columns.str.lower()
    faltando = [coluna for coluna in COLUNAS_OBRIGATORIAS if coluna not in df.columns]

    if faltando:
        return [], ("Faltam colunas obrigatórias: " + ", ".join(faltando))

    df["manchete"] = df["manchete"].fillna("").str.strip()
    df["url"] = df["url"].fillna("").str.strip()

    if "data" in df.columns:
        df["data"] = pd.to_datetime(df["data"], dayfirst=True, errors="coerce")
    else:
        df["data"] = pd.NaT

    if "palavras" in df.columns:
        df["palavras"] = (
            pd.to_numeric(df["palavras"], errors="coerce").fillna(0).astype(int)
        )
    else:
        df["palavras"] = 0

    if "fonte" in df.columns:
        df["fonte"] = df["fonte"].fillna("Enviado pelo usuário.").str.strip()
        df.loc[df["fonte"] == "", "fonte"] = "Enviado pelo usuário."
    else:
        df["fonte"] = "Enviado pelo usuário."

    if "texto" in df.columns:
        df["texto"] = df["texto"].fillna("").astype(str).str.strip()
    else:
        df["texto"] = ""

    df = df[["fonte", "manchete", "data", "palavras", "url", "texto"]]
    return df.to_dict(orient="records"), None


def padronizar_texto_enviado(df):
    df["full_text"] = df["titulo"] + "\n" + df["texto"]
    df["full_text"] = df["full_text"].str.lower().str.strip().apply(unidecode)
    df["full_text"] = df["full_text"].str.replace(r"[^\w\s]", "", regex=True)
    pass
