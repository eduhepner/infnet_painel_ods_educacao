import streamlit as st

st.title("📚 Painel ODS - Educação Brasil")

st.divider()

st.markdown("""
##### **Problema de negócio**  
É importante compreender as condições e desigualdades existentes na educação brasileira.  
Entretanto, os dados estão distribuídos em diferentes pesquisas e bases, o que pode dificultar sua consulta e comparação por pessoas sem conhecimento técnico.  
Essa dificuldade compromete a capacidade de identificar os problemas e desigualdades na educação, e dificulta a tomada de 
decisões baseada em dados. 
""")

st.markdown("""
##### **Objetivo do projeto**  
Desenvolver uma aplicação interativa utilizando Streamlit para facilitar a consulta, visualização e comparação de indicadores relacionados à educação brasileira provenientes de fontes públicas.
 * Coletar dados de fontes públicas relacionadas à educação;
 * Integrar dados provenientes de APIs e outras fontes;
 * Disponibilizar os dados tratados e agregados;
 * Facilitar a identificação de desigualdades e problemas relacionados à educação.
""")

st.markdown("""
##### **Links úteis e inspirações**  
* [IBGE — Indicadores e dados estatísticos](https://servicodados.ibge.gov.br/) 
* [INEP — Indicadores Educacionais](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/indicadores-educacionais/) 
* [UNICEF - Painel de dados](https://www.unicef.org/brazil/painel-de-dados)
* [MEC - Plano de Ações Articuladas](https://novopar.mec.gov.br/publico/painel/escolas)
* [World Bank — Education Statistics Dashboards](https://datatopics.worldbank.org/education/wDashboard/dqlearning)
""")

st.info("Selecione uma página no menu da esquerda para começar.")
