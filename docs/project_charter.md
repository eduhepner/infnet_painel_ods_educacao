# Project Charter — Aplicação de Indicadores Educacionais Brasileiros

## 1. Identificação do Projeto

**Nome do projeto:** Aplicação de Indicadores Educacionais Brasileiros (Painel ODS - Educação Brasil)

**Área:** Educação, Políticas Públicas e Sustentabilidade (ESG)

**ODS e Pilares ESG Atendidos:**
* **ODS 4 — Educação de Qualidade (Pilar Social - ESG):** Monitora taxas de alfabetização, escolarização, frequência ajustada e conclusão de ensino por Unidade Federativa e faixa etária, subsidiando diagnósticos de acesso e permanência escolar.
* **ODS 5 — Igualdade de Gênero (Pilar Social - ESG):** Desagrega todos os indicadores educacionais por sexo, permitindo identificar assimetrias de desempenho e evasão entre homens e mulheres.
* **ODS 10 — Redução das Desigualdades (Pilar Social - ESG):** Desagrega os indicadores por cor/raça, expondo disparidades estruturais históricas entre grupos populacionais nos estados brasileiros.
* **Governança de Dados e Transparência (Pilar Governança - ESG):** Integra exclusivamente fontes públicas auditáveis (IBGE, EBC, G1) com rastreabilidade de origem, timestamp de coleta e modelos de IA restritos aos dados oficiais.

**Tecnologia principal:** Python, Streamlit, FastAPI, Pandas, Altair, Google Gemini API (`gemini-3.5-flash-lite`) e HuggingFace Transformers (`ptt5-base-summ-cstnews`).

**Fontes de dados:** Bases públicas e oficiais da API de Agregados do IBGE (SIDRA), portais jornalísticos (Agência Brasil e G1) via *web scraping*, e arquivos CSV enviados pelos usuários.

---

## 2. Problema de Negócio

Compreender as condições e desigualdades existentes na educação brasileira é essencial para a formulação de políticas públicas e iniciativas sociais eficazes. Entretanto, os dados oficiais encontram-se dispersos em diferentes pesquisas, tabelas e agregados estatísticos, exigindo conhecimento técnico para extração, cruzamento e interpretação.

Essa barreira técnica compromete a capacidade de gestores, pesquisadores e organizações identificarem gargalos educacionais e tomarem decisões orientadas por dados.

A aplicação resolve esse problema ao centralizar os dados e responder, de forma visual e prática, a questões estratégicas como:
* Quais estados e regiões apresentam os indicadores educacionais mais preocupantes?
* Onde estão as maiores disparidades entre homens e mulheres ou entre diferentes grupos de cor/raça?
* Como cada faixa etária se comporta em relação à frequência escolar ideal e à conclusão do ensino?
* Quais temas e acontecimentos recentes estão pautando o debate educacional no país?
* Onde podem ser necessárias ações específicas para melhorar determinados indicadores?

---

## 3. Alinhamento Estratégico: Dados, IA e ESG

No contexto de Ciência de Dados aplicada ao setor público , a combinação entre **dados reais estruturados** e **modelos de Inteligência Artificial** transforma um painel descritivo tradicional em uma ferramenta ativa de apoio à decisão:

* **Uso de Dados Reais e Auditáveis:** Todos os indicadores provêm diretamente da API oficial do IBGE, eliminando suposições e garantindo rigor estatístico na avaliação dos critérios sociais (ESG).
* **Papel da Inteligência Artificial Generativa e NLP:**
  * *Sumarização de Notícias (PTT5):* Reduz a sobrecarga informacional ao sintetizar automaticamente matérias extensas coletadas da imprensa, conectando os números estatísticos ao contexto atual da educação.
  * *Assistente Conversacional Analítico (Gemini 3.5 Flash-Lite):* Democratiza o acesso aos dados ao permitir que usuários não técnicos façam perguntas complexas em português (ex.: rankings estaduais, comparações entre recortes demográficos) e recebam insights imediatos.
* **Engenharia de Prompts e Confiabilidade (Governança de IA):**
  * *Aterramento Estrito (Grounding):* As tabelas tratadas (`df_sexo` e `df_cor`) são serializadas em formato CSV e injetadas no *System Prompt* com regras rígidas que proíbem o modelo de usar conhecimento externo ou inventar números (mitigação de alucinações).
  * *Controle de Determinismo e Contexto:* Uso de `temperature=0.1` para precisão matemática, instruções explícitas para verificação de recortes etários (`Grupo de idade` / `Faixa etária ideal`) e **memória conversacional de curto prazo** (janela deslizante das últimas interações isolada por página), permitindo perguntas de acompanhamento (ex.: *"e em São Paulo?"*) com baixo custo computacional.

---

## 4. Ciclo de Ciência de Dados (Metodologia TDSP)

O desenvolvimento do projeto seguiu as etapas do *Team Data Science Process* (TDSP):

1. **Entendimento do Negócio:** Mapeamento das dores de acesso a indicadores educacionais e alinhamento com as metas dos ODS 4, 5 e 10.
2. **Aquisição e Compreensão dos Dados:** Construção de coletores automatizados para a API do IBGE (`requests` com cache de resiliência) e *scrapers* (`BeautifulSoup` e `Selenium` respeitando `robots.txt`), documentados no *Data Summary Report*.
3. **Preparação e Engenharia de Dados:** Padronização de esquemas, tratamento de codificações, filtragem regional/etária com `pandas` e exposição via API RESTful (`FastAPI`).
4. **Modelagem:** Integração do modelo `PTT5` para sumarização textual e configuração do `Gemini 3.5 Flash-Lite` com prompts aterrados e memória.
5. **Implantação e Geração de Insights:** Entrega do dashboard interativo em `Streamlit` com gráficos comparativos (`Altair`), exportação de dados e assistente conversacional em tempo real.

---

## 5. Objetivo Geral

Desenvolver uma aplicação interativa utilizando **Python, Streamlit e FastAPI** para facilitar a consulta, visualização e comparação de indicadores relacionados à educação brasileira provenientes de fontes públicas,
potencializada por modelos de Inteligência Artificial para geração de resumos e insights em linguagem natural.

---

## 6. Objetivos Específicos

* Coletar dados estruturados de APIs públicas (IBGE) e dados não estruturados via *web scraping* da área da Educação;
* Integrar dados provenientes de APIs e outras fontes;
* Organizar e tratar os dados para análise;
* Disponibilizar os dados tratados por meio de uma API (`FastAPI`);
* Construir visualizações interativas que evidenciem desigualdades regionais, de gênero e de cor/raça;
* Exibir e sumarizar automaticamente notícias recentes sobre educação;
* Disponibilizar um assistente conversacional com IA para auxiliar na interpretação dos indicadores e na geração de insights em linguagem natural.

---

## 7. Escopo

* Coleta automatizada de indicadores educacionais via API do IBGE com mecanismo de cache;
* Coleta de dados por meio de web scraping em páginas estáticas, quando permitido;
* Coleta de dados por meio de web scraping em páginas dinâmicas, quando permitido;
* Tratamento, validação e organização dos dados;
* Análise exploratória dos dados;
* Desenvolvimento de API própria.
* Desenvolvimento da aplicação utilizando Streamlit;
* Desenvolvimento de dashboard interativo (`Streamlit`) com filtros dinâmicos, métricas, gráficos, nuvem de palavras e download;
* Uso de LLMs para resumir notícias.
* Implementação de assistente conversacional (LLM) com memória de contexto para suporte à análise exploratória.

---

## 8. Metas

A principal meta do projeto é entregar uma plataforma analítica funcional que transforme dados públicos brutos em conhecimento acionável para governança educacional, permitindo que o usuário:
* Consulte indicadores educacionais sem precisar conhecer a estrutura técnica das APIs do IBGE;
* Compare estados, regiões, gêneros e grupos de cor/raça por meio de gráficos e tabelas dinâmicas;
* Consuma e envie dados estruturados por meio de uma API RESTful funcional;
* Obtenha resumos automáticos das principais notícias sobre educação;
* Converse com os dados em tempo real por meio de um assistente de IA com memória, extraindo rankings e insights sem necessidade de programação ou manipulação de planilhas.

---

## 9. Indicadores de Sucesso

| **KPI**               | **Como medimos**                                          | **Meta** |
| --------------------- | --------------------------------------------------------- | -------- |
| Cobertura de fontes   | nº de fontes de notícias disponíveis no painel            | ≥ 3      |
| Extração de notícias em páginas dinâmicas | capacidade de carregar e processar notícias de páginas dinâmicas | sim |
| Cobertura de notícias | nº de notícias carregadas e processadas                   | ≥ 20    |
| Atualidade            | diferença entre a data da coleta e a notícia mais recente | ≤ 7 dias |
| Qualidade dos dados   | % de notícias com URL e manchete válidas                  | ≥ 95%    |
| Cobertura de indicadores | nº de dimensões educacionais do IBGE integradas | 4 (Alfabetização, Escolarização, Frequência, Conclusão) |
| Visualização          | nº de visualizações disponíveis para análise              | ≥ 3      |
| Interatividade        | nº de filtros disponíveis   por página                    | ≥ 2      |
| API funcional         | endpoints GET e POST operando com validação               | sim      |
| LLM funcional (notícias)        | llm em pleno funcionamento para resumo de notícias        | sim      |
| Assistente conversacional        | chat integrado com memória de contexto respondendo com base nos dados do painel        | sim      |

---

## 10. Stakeholders

* Gestores da área de educação;
* Organizações não governamentais (ONGs);
* Pesquisadores, jornalistas de dados e cidadãos interessados no monitoramento dos ODS.

---

## 11. Entregável

O principal entregável do projeto será uma aplicação web interativa desenvolvida em **Python utilizando Streamlit**, capaz de consultar, organizar e visualizar indicadores educacionais provenientes de fontes públicas, integrada a uma API própria e a um assistente conversacional baseado em Inteligência Artificial (LLM) com memória de contexto para suporte à análise e geração de insights em tempo real.


O entregável final do projeto é uma solução completa de Ciência de Dados composta por:
1. **Pipeline de Coleta e Transformação (`src/`):** Scripts modulares de extração via API, *web scraping* e limpeza de dados;
2. **API RESTful (`api/main.py`):** Serviço em FastAPI documentado com endpoints para indicadores, notícias e sumarização por IA;
3. **Aplicação Web Interativa (`Streamlit`):** Dashboard multipáginas com filtros dinâmicos, visualizações em Altair, nuvem de palavras, exportação CSV, painel executivo consolidado via IA e assistente conversacional baseado em LLM (`Gemini 3.5 Flash-Lite`) para geração de insights em tempo real;
4. **Documentação TSDP:** *Project Charter* e *Data Summary Report* atualizados e alinhados ao ciclo de vida do projeto.