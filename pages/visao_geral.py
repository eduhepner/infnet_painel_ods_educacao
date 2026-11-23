import os

import altair as alt
import pandas as pd
import requests
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
API_BASE_URL = "http://127.0.0.1:8000"

st.title("🧭 Ciclo de Ciência de Dados, IA e Governança (ODS)")
st.caption(
    "Visão consolidada do pipeline: da coleta de dados públicos (IBGE e Notícias) à geração de insights e recomendações estratégicas via IA."
)
st.divider()


# ==============================================================================
# 1. CAMADA DE COLETA E CONSOLIDAÇÃO (API FASTAPI -> DATAFRAMES)
# ==============================================================================
@st.cache_data(ttl=3600, show_spinner=False)
def carregar_indicador(endpoint: str, tipo: str) -> pd.DataFrame:
    try:
        resp = requests.get(
            f"{API_BASE_URL}/{endpoint}", params={"tipo": tipo}, timeout=60
        )
        resp.raise_for_status()
        return pd.DataFrame(resp.json().get("dados", []))
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=3600, show_spinner=False)
def carregar_noticias() -> tuple[pd.DataFrame, str]:
    try:
        resp = requests.get(f"{API_BASE_URL}/noticias", timeout=60)
        resp.raise_for_status()
        resultado = resp.json()

        df = pd.DataFrame(resultado.get("dados", []))
        metadados = resultado.get("metadados", {})
        fontes = ", ".join(metadados.get("fontes", []))
        coletado_em = metadados.get("coletado_em", "")
        info = f"Fontes: {fontes} (coletado em {coletado_em})" if coletado_em else ""

        return df, info
    except Exception as erro:
        st.error(f"Erro ao carregar notícias: {erro}")
        return pd.DataFrame(), ""


def resumir_por_regiao(
    df: pd.DataFrame, nome_indicador: str, coluna_grupo: str
) -> pd.DataFrame:
    """Agrega a média por Região, recorte demográfico (Sexo/Cor) e grupo etário/etapa (se existir)."""
    if df.empty or "Região" not in df.columns or coluna_grupo not in df.columns:
        return pd.DataFrame()

    colunas_numericas = df.select_dtypes(include="number").columns
    if len(colunas_numericas) == 0:
        return pd.DataFrame()
    col_valor = colunas_numericas[-1]

    # Detecta se o indicador possui coluna de grupo etário ou faixa ideal
    col_etaria = next(
        (c for c in df.columns if "idade" in c.lower() or "faixa" in c.lower()),
        None,
    )

    colunas_agrupamento = ["Região", coluna_grupo]
    if col_etaria:
        colunas_agrupamento.append(col_etaria)

    resumo = (
        df.groupby(colunas_agrupamento, as_index=False)[col_valor]
        .mean()
        .round(2)
        .rename(columns={col_valor: "Taxa Média (%)", coluna_grupo: "Recorte"})
    )
    resumo["Indicador"] = nome_indicador
    resumo["Grupo Etário / Etapa"] = (
        resumo[col_etaria] if col_etaria else "População Geral (15+ anos)"
    )
    if col_etaria:
        resumo = resumo.drop(columns=[col_etaria])

    return resumo


with st.spinner("Consolidando dados coletados e tratados pela API..."):
    indicadores_config = {
        "Alfabetização (15+ anos)": "alfabetizacao",
        "Escolarização": "escolarizacao",
        "Frequência Escolar": "frequencia",
        "Conclusão de Ensino": "conclusao",
    }

    dfs_sexo = {
        nome: carregar_indicador(ep, "sexo") for nome, ep in indicadores_config.items()
    }
    dfs_cor = {
        nome: carregar_indicador(ep, "cor") for nome, ep in indicadores_config.items()
    }
    df_noticias, info_noticias = carregar_noticias()

    # Consolidação regional para visualização e contexto da IA
    lista_resumos_sexo = [
        resumir_por_regiao(df, nome, "Sexo") for nome, df in dfs_sexo.items()
    ]
    df_consolidado_sexo = (
        pd.concat([d for d in lista_resumos_sexo if not d.empty], ignore_index=True)
        if any(not d.empty for d in lista_resumos_sexo)
        else pd.DataFrame()
    )

    # Detecta dinamicamente o nome da coluna de cor/raça no DataFrame
    lista_resumos_cor = []
    for nome, df in dfs_cor.items():
        col_cor = next(
            (c for c in df.columns if "cor" in c.lower() or "raça" in c.lower()), None
        )
        if col_cor:
            lista_resumos_cor.append(resumir_por_regiao(df, nome, col_cor))
    df_consolidado_cor = (
        pd.concat([d for d in lista_resumos_cor if not d.empty], ignore_index=True)
        if any(not d.empty for d in lista_resumos_cor)
        else pd.DataFrame()
    )


# ==============================================================================
# 2. DEMONSTRAÇÃO DO CICLO DE CIÊNCIA DE DADOS (TDSP)
# ==============================================================================
st.subheader("1. Pipeline de Ciência de Dados (Coleta → Processamento → IA)")

c1, c2, c3, c4 = st.columns(4)
c1.info(
    "**1. Coleta (ETL & Scraping)**\n\n"
    "• 8 tabelas oficiais da API IBGE\n"
    "• Portais EBC e G1 (`robots.txt`)"
)
c2.info(
    "**2. Processamento & API**\n\n"
    "• Limpeza/tipagem com `pandas`\n"
    "• Validação `Pydantic` + `FastAPI`"
)
c3.info(
    "**3. Modelos de IA**\n\n"
    "• `PTT5`: sumarização de notícias\n"
    "• `Gemini 3.5`: insights e chat"
)
c4.info(
    "**4. Governança & ESG**\n\n"
    "• Monitoramento ODS 4, 5 e 10\n"
    "• Respostas aterradas em dados reais"
)

total_registros_ibge = sum(len(df) for df in dfs_sexo.values()) + sum(
    len(df) for df in dfs_cor.values()
)
m1, m2, m3 = st.columns(3)
m1.metric("Registros IBGE Processados", f"{total_registros_ibge:,}".replace(",", "."))
m2.metric("Indicadores Educacionais (ODS 4)", "4 dimensões (Sexo e Cor/Raça)")
m3.metric("Notícias Coletadas (Total)", len(df_noticias))

tab_dados_sexo, tab_dados_cor, tab_noticias, tab_arquitetura = st.tabs(
    [
        "📊 Consolidado por Sexo (ODS 5)",
        "📊 Consolidado por Cor/Raça (ODS 10)",
        "📰 Notícias Processadas",
        "🤖 Como a IA transforma os dados",
    ]
)

with tab_dados_sexo:
    if not df_consolidado_sexo.empty:
        st.dataframe(df_consolidado_sexo, width="stretch", hide_index=True)
    else:
        st.warning(
            "Dados por sexo indisponíveis. Verifique se a API FastAPI está rodando."
        )

with tab_dados_cor:
    if not df_consolidado_cor.empty:
        st.dataframe(df_consolidado_cor, width="stretch", hide_index=True)
    else:
        st.warning(
            "Dados por cor/raça indisponíveis. Verifique se a API FastAPI está rodando."
        )

with tab_noticias:
    if not df_noticias.empty:
        st.dataframe(df_noticias.head(15), width="stretch", hide_index=True)
    else:
        st.info("Nenhuma notícia carregada no endpoint `/noticias`.")

with tab_arquitetura:
    st.markdown("""
        * **Sumarização de Texto (`recogna-nlp/ptt5-base-summ-cstnews`):** Recebe o texto bruto extraído via *web scraping* e sintetiza os fatos principais da notícia educacional via endpoint `GET /noticias/resumir`.
        * **Diagnóstico Estruturado (`gemini-3.5-flash-lite` + JSON Schema):** Cruza as médias regionais dos 4 indicadores (Alfabetização, Escolarização, Frequência e Conclusão) para calcular prioridades de intervenção e gerar recomendações de políticas públicas.
        * **Assistente Conversacional com Memória (`st.session_state`):** Injeta os dados tratados em formato CSV nas instruções de sistema (*grounding*), mantendo janela deslizante de contexto para análises em tempo real sem alucinações.
        """)

st.divider()


# ==============================================================================
# 3. VISUALIZAÇÕES E RECOMENDAÇÕES GERADAS PELA IA (SAÍDA ESTRUTURADA)
# ==============================================================================
st.subheader("2. Resultados, Gráficos e Recomendações Gerados pela IA")
st.caption(
    "O modelo Gemini analisa simultaneamente os 4 indicadores consolidados para classificar a criticidade regional e propor ações alinhadas aos ODS."
)


class PrioridadeRegionalIA(BaseModel):
    regiao: str
    indice_prioridade_ia: int
    principal_desigualdade: str
    recomendacao_acao: str


class RelatorioEstrategicoIA(BaseModel):
    sintese_executiva: str
    prioridades_regionais: list[PrioridadeRegionalIA]
    recomendacao_ods4: str
    recomendacao_ods5: str
    recomendacao_ods10: str


@st.cache_resource
def obter_cliente_gemini():
    return genai.Client(api_key=GEMINI_API_KEY)


if st.button("✨ Gerar Diagnóstico e Gráficos com IA", type="primary"):
    if not GEMINI_API_KEY:
        st.error("Chave GEMINI_API_KEY não encontrada no arquivo .env.")
    elif df_consolidado_sexo.empty or df_consolidado_cor.empty:
        st.warning("Carregue os dados da API antes de executar a análise da IA.")
    else:
        with st.spinner("Analisando indicadores e gerando matriz de prioridade ESG..."):
            try:
                client = obter_cliente_gemini()
                prompt_diagnostico = f"""
                Você é um especialista em Políticas Públicas Educacionais, Governança e Sustentabilidade (ESG / ODS 4, 5 e 10).
                Analise os dois resumos regionais consolidados abaixo (médias por Região, Indicador, Sexo e Cor/Raça) e gere um diagnóstico estruturado:

                1. `sintese_executiva`: Um parágrafo objetivo resumindo o panorama educacional brasileiro a partir desses números.
                2. `prioridades_regionais`: Para cada uma das 5 regiões (Norte, Nordeste, Centro-Oeste, Sudeste, Sul), atribua um `indice_prioridade_ia` de 0 a 100 (onde 100 = maior urgência de intervenção devido a menores taxas ou maiores desigualdades), aponte a `principal_desigualdade` observada nos dados e sugira uma `recomendacao_acao` prática.
                3. `recomendacao_ods4`: Recomendação estratégica focada em qualidade e permanência escolar (ODS 4).
                4. `recomendacao_ods5`: Recomendação focada em equidade de gênero com base nas diferenças entre homens e mulheres observadas (ODS 5).
                5. `recomendacao_ods10`: Recomendação focada em redução das desigualdades raciais com base nas diferenças por cor/raça observadas (ODS 10).

                === RESUMO POR SEXO ===
                {df_consolidado_sexo.to_csv(index=False)}

                === RESUMO POR COR/RAÇA ===
                {df_consolidado_cor.to_csv(index=False)}
                """

                resposta = client.models.generate_content(
                    model="gemini-3.5-flash-lite",
                    contents=prompt_diagnostico,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=RelatorioEstrategicoIA,
                        temperature=0.1,
                    ),
                )
                st.session_state["relatorio_ia_geral"] = (
                    RelatorioEstrategicoIA.model_validate_json(resposta.text)
                )
            except Exception as erro:
                st.error(f"Erro ao gerar diagnóstico com Gemini: {erro}")

if "relatorio_ia_geral" in st.session_state:
    relatorio = st.session_state["relatorio_ia_geral"]

    st.info(f"**Síntese Executiva da IA:** {relatorio.sintese_executiva}")

    df_prioridade = pd.DataFrame(
        [item.model_dump() for item in relatorio.prioridades_regionais]
    )

    col_graf, col_tab = st.columns([1.1, 1.3])
    with col_graf:
        st.markdown("**Índice de Prioridade de Intervenção (Gerado pela IA)**")
        grafico_ia = (
            alt.Chart(df_prioridade)
            .mark_bar(cornerRadiusTopRight=6, cornerRadiusBottomRight=6)
            .encode(
                x=alt.X(
                    "indice_prioridade_ia:Q",
                    title="Índice de Urgência (0–100)",
                    scale=alt.Scale(domain=[0, 100]),
                ),
                y=alt.Y("regiao:N", sort="-x", title="Região"),
                color=alt.Color(
                    "indice_prioridade_ia:Q",
                    scale=alt.Scale(scheme="orangered"),
                    legend=None,
                ),
                tooltip=["regiao", "indice_prioridade_ia", "principal_desigualdade"],
            )
            .properties(height=260)
        )
        st.altair_chart(grafico_ia, width="stretch")

    with col_tab:
        st.markdown("**Plano de Ação Regional Sugerido pela IA**")
        st.dataframe(
            df_prioridade.rename(
                columns={
                    "regiao": "Região",
                    "indice_prioridade_ia": "Prioridade (0-100)",
                    "principal_desigualdade": "Gargalo Detectado",
                    "recomendacao_acao": "Ação Recomendada",
                }
            ),
            width="stretch",
            hide_index=True,
        )

    st.markdown("**Recomendações Estratégicas por Pilar ODS / ESG**")
    o1, o2, o3 = st.columns(3)
    o1.success(f"**🎯 ODS 4 — Educação de Qualidade**\n\n{relatorio.recomendacao_ods4}")
    o2.success(f"**⚖️ ODS 5 — Igualdade de Gênero**\n\n{relatorio.recomendacao_ods5}")
    o3.success(
        f"**🤝 ODS 10 — Redução das Desigualdades**\n\n{relatorio.recomendacao_ods10}"
    )

st.divider()


# ==============================================================================
# 4. INTERAÇÃO EM TEMPO REAL: CONSULTOR DE GOVERNANÇA & SUSTENTABILIDADE (ESG)
# ==============================================================================
col_chat_titulo, col_chat_limpar = st.columns([5, 1])
with col_chat_titulo:
    st.subheader("3. Consultor Interativo de Governança e Sustentabilidade (ESG / ODS)")
    st.caption(
        "Converse em tempo real com a IA sobre todos os indicadores consolidados e políticas públicas."
    )
with col_chat_limpar:
    if st.button("🗑️ Limpar", key="limpar_chat_geral", use_container_width=True):
        st.session_state.pop("historico_chat_geral", None)
        st.rerun()

if not GEMINI_API_KEY:
    st.error("Chave GEMINI_API_KEY não encontrada no arquivo .env.")
elif df_consolidado_sexo.empty or df_consolidado_cor.empty:
    st.warning("Aguardando carregamento dos dados da API para ativar o consultor.")
else:
    if "historico_chat_geral" not in st.session_state:
        st.session_state.historico_chat_geral = []

    box_chat = st.container(height=360)
    with box_chat:
        if not st.session_state.historico_chat_geral:
            st.info(
                "Pergunte algo estratégico, por exemplo: *Quais ações de governança priorizar no Nordeste considerando os indicadores de cor/raça (ODS 10) e frequência escolar?*"
            )
        for msg in st.session_state.historico_chat_geral:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    with st.form("form_chat_geral_esg", clear_on_submit=True, border=False):
        col_input, col_send = st.columns([6, 1])
        pergunta = col_input.text_input(
            "Pergunta ESG",
            placeholder="Faça sua pergunta sobre sustentabilidade, governança educacional ou ODS...",
            label_visibility="collapsed",
        )
        enviar = col_send.form_submit_button("Enviar ➤", use_container_width=True)

    if enviar and pergunta:
        st.session_state.historico_chat_geral.append(
            {"role": "user", "content": pergunta}
        )

        with box_chat:
            with st.chat_message("user"):
                st.markdown(pergunta)

            with st.chat_message("assistant"):
                with st.spinner(
                    "Consultando indicadores consolidados e diretrizes ODS..."
                ):
                    try:
                        client = obter_cliente_gemini()
                        instrucoes_esg = f"""Você é um consultor especialista em Governança Pública, Sustentabilidade (ESG) e Objetivos de Desenvolvimento Sustentável (ODS 4, 5 e 10) da ONU aplicados à educação brasileira.

REGRAS ESTRITAS:
1. Baseie suas respostas exclusivamente nos dados consolidados fornecidos abaixo (médias regionais dos 4 indicadores do IBGE: Alfabetização, Escolarização, Frequência Escolar e Conclusão de Ensino).
2. Conecte sempre os números observados aos pilares de Sustentabilidade e Governança (transparência, alocação eficiente de recursos públicos, equidade de gênero - ODS 5 e equidade racial - ODS 10).
3. Não invente dados ou estatísticas ausentes nas tabelas. Se o dado não estiver disponível, informe com clareza.
4. Mantenha a coerência com o histórico recente da conversa.
5. Seja objetivo, estruturado e responda em português.

=== INDICADORES CONSOLIDADOS POR REGIÃO E SEXO (ODS 4 e 5) ===
{df_consolidado_sexo.to_csv(index=False)}

=== INDICADORES CONSOLIDADOS POR REGIÃO E COR/RAÇA (ODS 4 e 10) ===
{df_consolidado_cor.to_csv(index=False)}
"""
                        # Mantém memória das últimas 4 perguntas e 4 respostas (8 mensagens)
                        historico_api = [
                            types.Content(
                                role="model" if m["role"] == "assistant" else "user",
                                parts=[types.Part.from_text(text=m["content"])],
                            )
                            for m in st.session_state.historico_chat_geral[-8:]
                        ]

                        resposta_chat = client.models.generate_content(
                            model="gemini-3.5-flash-lite",
                            contents=historico_api,
                            config=types.GenerateContentConfig(
                                system_instruction=instrucoes_esg,
                                temperature=0.2,
                            ),
                        )
                        texto = resposta_chat.text
                        st.markdown(texto)
                        st.session_state.historico_chat_geral.append(
                            {"role": "assistant", "content": texto}
                        )
                    except Exception as erro:
                        st.error(f"Erro na consulta ao Gemini: {erro}")
