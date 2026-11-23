import os

import pandas as pd
import requests
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

from src.data_access import (
    buscar_taxa_frequencia_cor,
    buscar_taxa_frequencia_sexo,
)
from src.graphics import frequencia_cor, frequencia_sexo
from src.transform import filtrar, ordenar

# Carrega as variáveis do arquivo .env (GEMINI_API_KEY)
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

st.title("📚 Painel ODS - Educação Brasil")
st.divider()


@st.cache_data(ttl=3600, show_spinner=False)
def obter_dados_sexo():
    try:
        resposta = requests.get(
            "http://127.0.0.1:8000/frequencia",
            params={"tipo": "sexo"},
            timeout=60,
        )

        resposta.raise_for_status()

        resultado = resposta.json()

        dados = pd.DataFrame(resultado["dados"])
        msg = resultado["metadados"]["coletado_em"]
        msg = "API do IBGE em " + msg

        return dados, msg

    except requests.Timeout:
        st.error("A API demorou demais para responder. Tente novamente.")

    except requests.HTTPError as erro:
        try:
            detalhe = erro.response.json().get("detail", str(erro))
        except ValueError:
            detalhe = str(erro)

        st.error(f"Erro {erro.response.status_code}: {detalhe}")

    return pd.DataFrame(), "Erro ao consultar a API"


@st.cache_data(ttl=3600, show_spinner=False)
def obter_dados_cor():
    try:
        resposta = requests.get(
            "http://127.0.0.1:8000/frequencia",
            params={"tipo": "cor"},
            timeout=60,
        )

        resposta.raise_for_status()

        resultado = resposta.json()

        dados = pd.DataFrame(resultado["dados"])
        msg = resultado["metadados"]["coletado_em"]
        msg = "API do IBGE em " + msg

        return dados, msg

    except requests.Timeout:
        st.error("A API demorou demais para responder. Tente novamente.")

    except requests.HTTPError as erro:
        try:
            detalhe = erro.response.json().get("detail", str(erro))
        except ValueError:
            detalhe = str(erro)

        st.error(f"Erro {erro.response.status_code}: {detalhe}")

    return pd.DataFrame(), "Erro ao consultar a API"


@st.cache_resource
def obter_cliente_gemini():
    return genai.Client(api_key=GEMINI_API_KEY)


def montar_instrucoes_frequencia(df_sexo: pd.DataFrame, df_cor: pd.DataFrame) -> str:
    dados_sexo_csv = df_sexo.to_csv(index=False)
    dados_cor_csv = df_cor.to_csv(index=False)

    return f"""Você é um analista de dados especializado nos indicadores de educação (ODS) do IBGE exibidos neste painel.

REGRAS ESTRITAS:
1. Responda EXCLUSIVAMENTE com base nas duas tabelas de dados fornecidas abaixo (`df_sexo` e `df_cor`), referentes à taxa ajustada de frequência escolar.
2. Nunca utilize conhecimento externo, estimativas ou dados que não estejam explicitamente presentes ou calculáveis a partir dessas tabelas.
3. Atenção à coluna `Faixa etária ideal por curso frequentado`: sempre verifique a faixa etária correspondente ao responder rankings ou comparações (e deixe claro na resposta qual faixa etária/curso foi considerado).
4. Se o usuário fizer uma pergunta cuja resposta não esteja nos dados fornecidos, informe educadamente que você só pode responder com base nos dados de frequência escolar carregados no painel.
5. Mantenha o contexto das perguntas anteriores da conversa (por exemplo, se o usuário perguntar "e São Paulo?" após perguntar sobre um ranking, aplique o mesmo critério e faixa etária da pergunta anterior).
6. Seja direto, preciso e responda em português.

=== TABELA 1: TAXA DE FREQUÊNCIA ESCOLAR POR ESTADO, FAIXA ETÁRIA E SEXO (df_sexo) ===
{dados_sexo_csv}

=== TABELA 2: TAXA DE FREQUÊNCIA ESCOLAR POR ESTADO, FAIXA ETÁRIA E COR/RAÇA (df_cor) ===
{dados_cor_csv}
"""


with st.spinner("Coletando dados do IBGE…"):
    df_sexo, msg_sexo = obter_dados_sexo()
    df_cor, msg_cor = obter_dados_cor()

st.header("Taxa ajustada de frequência escolar")

with st.sidebar:
    st.subheader("Filtros")

    with st.form("filtros_frequencia"):

        regioes = sorted(df_sexo["Região"].unique())

        if "regioes_select" not in st.session_state:
            st.session_state.regioes_select = regioes

        if "opcao_ordem" not in st.session_state:
            st.session_state.opcao_ordem = "Estado (A-Z)"

        if "mostrar_tabela" not in st.session_state:
            st.session_state.mostrar_tabela = False

        if "faixa_etaria_frequencia" not in st.session_state:
            st.session_state.faixa_etaria_frequencia = df_sexo[
                "Faixa etária ideal por curso frequentado"
            ].iloc[0]

        if "taxa_frequencia" not in st.session_state:
            st.session_state.taxa_frequencia = 0

        regioes_select = st.multiselect(
            "Regiões",
            regioes,
            default=st.session_state.regioes_select,
            key="freq_regioes",
        )

        faixas_etarias = df_sexo["Faixa etária ideal por curso frequentado"].unique()

        faixa_etaria = st.selectbox(
            "Faixa etária ideal por curso frequentado",
            faixas_etarias,
            key="faixa_etaria_frequencia",
        )

        taxa_minima = st.slider(
            "Taxa de frequência mínima",
            min_value=0,
            max_value=100,
            step=1,
            key="taxa_frequencia",
        )

        opcoes_ordem = ["Estado (A-Z)", "Região (A-Z)"]

        opcao_ordem = st.radio(
            "Ordenar por",
            opcoes_ordem,
            index=opcoes_ordem.index(st.session_state.opcao_ordem),
            key="freq_ordem",
        )

        mostrar_tabela = st.checkbox(
            "Mostrar as tabelas de dados",
            value=st.session_state.mostrar_tabela,
            key="freq_tabela",
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

df_sexo_filtrado = filtrar(
    df_sexo,
    regioes_select=st.session_state.regioes_select,
    faixa_etaria=faixa_etaria,
    taxa_minima=taxa_minima,
)

df_cor_filtrado = filtrar(
    df_cor,
    regioes_select=st.session_state.regioes_select,
    faixa_etaria=faixa_etaria,
    taxa_minima=taxa_minima,
)

df_sexo_ordenado = ordenar(
    df_sexo_filtrado,
    opcao_ordem=st.session_state.opcao_ordem,
)
df_cor_ordenado = ordenar(
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


st.markdown("### 📊 Frequência escolar por Estado e por Sexo")
st.caption(f"Fonte: {msg_sexo}")

grafico = frequencia_sexo(df_sexo_ordenado)
st.altair_chart(grafico, width="stretch")

if mostrar_tabela:
    st.dataframe(df_sexo_ordenado, width="stretch", hide_index=True)

    st.download_button(
        "⬇ Baixar tabela (csv)",
        data=df_sexo_ordenado.to_csv(),
        file_name="painel_ods_filtrado.csv",
        key="download_sexo",
    )

st.subheader("Frequência escolar por Estado e por Cor")
st.caption(f"Fonte: {msg_cor}")

grafico = frequencia_cor(df_cor_ordenado)
st.altair_chart(grafico, width="stretch")

if mostrar_tabela:
    st.dataframe(df_cor_ordenado, width="stretch", hide_index=True)

    st.download_button(
        "⬇ Baixar tabela (csv)",
        data=df_cor_ordenado.to_csv(),
        file_name="painel_ods_filtrado.csv",
        key="download_cor",
    )


# ==============================================================================
# ASSISTENTE CONVERSACIONAL FLUTUANTE (GEMINI COM MEMÓRIA DE 4 MENSAGENS)
# ==============================================================================
st.markdown(
    """
    <style>
    /* Fixa o botão do popover no canto inferior direito */
    div[data-testid="stPopover"] {
        position: fixed;
        bottom: 24px;
        right: 24px;
        z-index: 9999;
    }
    div[data-testid="stPopover"] > button {
        border-radius: 999px;
        padding: 0.6rem 1.2rem;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25);
        font-weight: 600;
    }
    /* Define uma largura confortável para a janela flutuante do chat */
    div[data-testid="stPopoverBody"] {
        width: 420px;
        max-width: 90vw;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.popover("💬 Assistente de Dados"):
    col_titulo, col_botao = st.columns([4, 1])
    with col_titulo:
        st.markdown("**Assistente de Frequência Escolar (IBGE)**")
        st.caption(
            "Pergunte sobre rankings, estados, faixa etária ideal, sexo ou cor/raça."
        )
    with col_botao:
        if st.button(
            "🗑️",
            key="limpar_chat_frequencia",
            help="Limpar histórico do chat",
            use_container_width=True,
        ):
            st.session_state.pop("historico_chat_frequencia", None)
            st.rerun()

    if df_sexo.empty or df_cor.empty:
        st.warning("Os dados do IBGE não foram carregados.")
    elif not GEMINI_API_KEY:
        st.error("Chave GEMINI_API_KEY não encontrada no arquivo .env.")
    else:
        if "historico_chat_frequencia" not in st.session_state:
            st.session_state.historico_chat_frequencia = []

        mensagens_box = st.container(height=350)

        with mensagens_box:
            if not st.session_state.historico_chat_frequencia:
                st.info(
                    "Olá! Pergunte algo como: *Qual a colocação do RJ na taxa de frequência escolar por sexo?*"
                )
            for mensagem in st.session_state.historico_chat_frequencia:
                with st.chat_message(mensagem["role"]):
                    st.markdown(mensagem["content"])

        with st.form(
            "form_chat_flutuante_frequencia", clear_on_submit=True, border=False
        ):
            col_in, col_btn = st.columns([5, 1])
            prompt = col_in.text_input(
                "Pergunta",
                placeholder="Digite sua pergunta e aperte Enter...",
                label_visibility="collapsed",
            )
            enviar = col_btn.form_submit_button("➤", use_container_width=True)

        if enviar and prompt:
            st.session_state.historico_chat_frequencia.append(
                {"role": "user", "content": prompt}
            )

            with mensagens_box:
                with st.chat_message("user"):
                    st.markdown(prompt)

                with st.chat_message("assistant"):
                    with st.spinner("Analisando os dados..."):
                        try:
                            client = obter_cliente_gemini()
                            instrucoes = montar_instrucoes_frequencia(df_sexo, df_cor)

                            # Envia apenas as últimas 4 mensagens para a API do Gemini
                            historico_recente = [
                                types.Content(
                                    role=(
                                        "model"
                                        if msg["role"] == "assistant"
                                        else "user"
                                    ),
                                    parts=[types.Part.from_text(text=msg["content"])],
                                )
                                for msg in st.session_state.historico_chat_frequencia[
                                    -4:
                                ]
                            ]

                            resposta = client.models.generate_content(
                                model="gemini-3.5-flash-lite",
                                contents=historico_recente,
                                config=types.GenerateContentConfig(
                                    system_instruction=instrucoes,
                                    temperature=0.1,
                                ),
                            )
                            texto_resposta = resposta.text

                            st.markdown(texto_resposta)
                            st.session_state.historico_chat_frequencia.append(
                                {"role": "assistant", "content": texto_resposta}
                            )
                        except Exception as erro:
                            st.error(f"Erro ao consultar a API do Gemini: {erro}")
