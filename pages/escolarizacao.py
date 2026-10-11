import streamlit as st

from src.data_access import (
    buscar_taxa_escolarizacao_cor,
    buscar_taxa_escolarizacao_sexo,
)
from src.graphics import escolarizacao_cor, escolarizacao_sexo
from src.transform import filtrar, ordenar

st.title("📚 Painel ODS - Educação Brasil")
st.divider()


@st.cache_data(ttl=3600, show_spinner=False)
def obter_dados_sexo():
    dados, msg = buscar_taxa_escolarizacao_sexo()
    return dados, msg


@st.cache_data(ttl=3600, show_spinner=False)
def obter_dados_cor():
    dados, msg = buscar_taxa_escolarizacao_cor()
    return dados, msg


with st.spinner("Coletando dados do IBGE…"):
    df_sexo, msg_sexo = obter_dados_sexo()
    df_cor, msg_cor = obter_dados_cor()

st.header("Taxa de escolarização")

with st.sidebar:
    st.subheader("Filtros")

    with st.form("filtros_escolarizacao"):

        regioes = sorted(df_sexo["Região"].unique())

        if "regioes_select" not in st.session_state:
            st.session_state.regioes_select = regioes

        if "opcao_ordem" not in st.session_state:
            st.session_state.opcao_ordem = "Estado (A-Z)"

        if "mostrar_tabela" not in st.session_state:
            st.session_state.mostrar_tabela = False

        if "grupo_idade_escolarizacao" not in st.session_state:
            st.session_state.grupo_idade_escolarizacao = df_sexo["Grupo de idade"].iloc[
                0
            ]

        if "taxa_escolarizacao" not in st.session_state:
            st.session_state.taxa_escolarizacao = 0

        regioes_select = st.multiselect(
            "Regiões",
            regioes,
            default=st.session_state.regioes_select,
            key="esc_regioes",
        )

        grupos_idade = df_sexo["Grupo de idade"].unique()

        grupo_idade = st.selectbox(
            "Grupo de idade",
            grupos_idade,
            key="grupo_idade_escolarizacao",
        )

        taxa_minima = st.slider(
            "Taxa de escolarização mínima",
            min_value=0,
            max_value=100,
            step=1,
            key="taxa_escolarizacao",
        )

        opcoes_ordem = ["Estado (A-Z)", "Região (A-Z)"]

        opcao_ordem = st.radio(
            "Ordenar por",
            opcoes_ordem,
            index=opcoes_ordem.index(st.session_state.opcao_ordem),
            key="esc_ordem",
        )

        mostrar_tabela = st.checkbox(
            "Mostrar as tabelas de dados",
            value=st.session_state.mostrar_tabela,
            key="esc_tabela",
        )

        aplicar = st.form_submit_button("Aplicar filtros")

    if aplicar:

        if regioes_select:
            st.session_state.regioes_select = regioes_select
        else:
            st.session_state.regioes_select = regioes

        st.session_state.opcao_ordem = opcao_ordem
        st.session_state.mostrar_tabela = mostrar_tabela

        st.success("Filtros aplicados.")

df_sexo_filtrado, df_cor_filtrado = filtrar(
    df_sexo,
    df_cor,
    regioes_select=st.session_state.regioes_select,
    grupo_idade=grupo_idade,
    taxa_minima=taxa_minima,
)

df_sexo_ordenado, df_cor_ordenado = ordenar(
    df_sexo_filtrado,
    df_cor_filtrado,
    opcao_ordem=st.session_state.opcao_ordem,
)

####### metricas
m1, m2 = st.columns(2)

n_regioes = df_sexo_ordenado["Região"].nunique()
if "regioes_old" not in st.session_state:
    st.session_state["regioes_old"] = n_regioes
delta = n_regioes - st.session_state["regioes_old"]
if delta == 0:
    delta = None
m1.metric(
    "Regiões",
    n_regioes,
    delta=delta,
)
st.session_state["regioes_old"] = n_regioes

n_estados = df_sexo_ordenado["Estado"].nunique()
if "estados_old" not in st.session_state:
    st.session_state["estados_old"] = n_estados
delta = n_estados - st.session_state["estados_old"]
if delta == 0:
    delta = None
m2.metric(
    "Estados",
    n_estados,
    delta=delta,
)
st.session_state["estados_old"] = n_estados


st.markdown("### 📊 Escolarização por Estado e por Sexo")
st.caption(f"Fonte: {msg_sexo}")

grafico = escolarizacao_sexo(df_sexo_ordenado)
st.altair_chart(grafico, width="stretch")

if mostrar_tabela:
    st.dataframe(df_sexo_ordenado, width="stretch", hide_index=True)

    st.download_button(
        "⬇ Baixar CSV do que está na tela",
        data=df_sexo_ordenado.to_csv(),
        file_name="painel_ods_filtrado.csv",
        key="download_sexo",
    )

st.subheader("Escolarização por Estado e por Cor")
st.caption(f"Fonte: {msg_cor}")

grafico = escolarizacao_cor(df_cor_ordenado)
st.altair_chart(grafico, width="stretch")

if mostrar_tabela:
    st.dataframe(df_cor_ordenado, width="stretch", hide_index=True)

    st.download_button(
        "⬇ Baixar CSV do que está na tela",
        data=df_cor_ordenado.to_csv(),
        file_name="painel_ods_filtrado.csv",
        key="download_cor",
    )
