import pandas as pd
import streamlit as st

from src.news_transform import (
    create_wordcloud,
    filtro_news,
    ler_csv_enviado,
    load_news,
    metrics_news,
    ordenar_news,
    processar_news,
)

st.title("📚 Painel ODS - Educação Brasil")
st.divider()


@st.cache_data(ttl=3600, show_spinner=False)
def obter_dados():
    df, texto = load_news()
    return df, texto


@st.cache_data(ttl=3600, show_spinner=False)
def gerar_wordcloud(palavras_significativas):
    fig = create_wordcloud(palavras_significativas)
    return fig


with st.spinner("Coletando noticias…"):
    df, texto = obter_dados()

st.header("📰 Publicações sobre Educação, na imprensa")


if "noticias_enviadas" not in st.session_state:
    st.session_state.noticias_enviadas = []

with st.expander("📤 Enviar um CSV de notícias"):
    st.caption(
        "Formato esperado: CSV - Colunas: `manchete` e `url` (obrigatórias). Opcionais: `fonte`, `data`, `palavras`, `texto` (corpo da noticia)."
    )
    enviado = st.file_uploader("Arquivo CSV", type="csv", key="csv_noticias")
    if enviado is not None:
        conteudo = enviado.getvalue()
        novas_noticias, erro = ler_csv_enviado(conteudo)
        if erro:
            st.error(f"ERRO: {erro}")
        else:
            urls_existentes = {
                noticia["url"] for noticia in st.session_state.noticias_enviadas
            }
            novas_noticias = [
                noticia
                for noticia in novas_noticias
                if noticia["url"] not in urls_existentes
            ]
            st.session_state.noticias_enviadas.extend(novas_noticias)


if st.session_state.noticias_enviadas:
    df_novas_noticias = pd.DataFrame(st.session_state.noticias_enviadas)
    novo_texto = df_novas_noticias["texto"].rename("full_text")
    df_novas_noticias = df_novas_noticias.drop(columns=["texto"])

    df = pd.concat([df, df_novas_noticias], ignore_index=True)
    texto = pd.concat([texto, novo_texto], ignore_index=True)

    duplicados = df.duplicated(subset="url")

    df = df.loc[~duplicados].reset_index(drop=True)
    texto = texto.loc[~duplicados].reset_index(drop=True)

with st.sidebar:
    st.subheader("Filtros")

    with st.form("filtros_noticias"):

        fontes = sorted(df["fonte"].unique())

        if "fontes_save" not in st.session_state:
            st.session_state.fontes_save = fontes

        fontes_select = st.multiselect(
            "Fontes de notícias",
            fontes,
            key="fontes_select",
            default=st.session_state.fontes_save,
        )

        opcao_ordem = st.radio(
            "Ordenar por",
            ["Mais recentes", "Mais antigas"],
            key="ordem_data",
        )

        aplicar = st.form_submit_button("Aplicar filtros")

    if aplicar:
        if fontes_select:
            st.session_state.fontes_save = fontes_select
        else:
            st.session_state.fontes_save = fontes
        st.success("Filtros aplicados.")


df_filtrado = filtro_news(df, fontes_select)
df_ordenado = ordenar_news(df_filtrado, opcao_ordem)


texto_filtrado = texto.loc[df_ordenado.index]
if texto_filtrado.empty:
    palavras_significativas = []
    fig = None
else:
    palavras_significativas = processar_news(texto_filtrado.iloc[:, 0])
    fig = gerar_wordcloud(palavras_significativas)


# m etricas
n_noticias, n_fontes, n_palavras, data_inicial, data_final = metrics_news(df_ordenado)
m1, m2, m3 = st.columns(3)

if "n_noticias_old" not in st.session_state:
    st.session_state["n_noticias_old"] = n_noticias
delta = n_noticias - st.session_state["n_noticias_old"]
if delta == 0:
    delta = None
m1.metric(
    "Notícias",
    n_noticias,
    delta=delta,
)
st.session_state["n_noticias_old"] = n_noticias

if "n_fontes_old" not in st.session_state:
    st.session_state["n_fontes_old"] = n_fontes
delta = n_fontes - st.session_state["n_fontes_old"]
if delta == 0:
    delta = None
m2.metric(
    "Fontes",
    n_fontes,
    delta=delta,
)
st.session_state["n_fontes_old"] = n_fontes

if "n_palavras_old" not in st.session_state:
    st.session_state["n_palavras_old"] = n_palavras
delta = n_palavras - st.session_state["n_palavras_old"]
if delta == 0:
    delta = None
m3.metric(
    "Palavras",
    n_palavras,
    delta=delta,
)
st.session_state["n_palavras_old"] = n_palavras


m4, m5, m6 = st.columns(3)

if pd.notna(data_inicial):
    data_inicial = data_inicial.strftime("%d/%m/%Y")
else:
    data_inicial = "Sem dados"

m4.metric("Notícia mais antiga", data_inicial)

if pd.notna(data_final):
    data_final = data_final.strftime("%d/%m/%Y")
else:
    data_final = "Sem dados"

m5.metric("Notícia mais recente", data_final)

m6.metric("Palavras significativas", len(palavras_significativas))


st.dataframe(df_ordenado, hide_index=True)
st.download_button(
    "⬇ Baixar tabela (csv)",
    data=df_ordenado.to_csv(),
    file_name="noticias.csv",
    key="noticias_download",
)

st.divider()
if palavras_significativas:
    qtd = st.slider("Quantas palavras mostrar", 5, 40, 20, step=5)
    frequencia = pd.DataFrame(
        palavras_significativas, columns=["palavra", "quantidade"]
    )
    frequencia = frequencia.iloc[:qtd, :]
    st.bar_chart(frequencia, x="palavra", y="quantidade")

st.divider()

if fig is not None:
    st.pyplot(fig, width="stretch")
