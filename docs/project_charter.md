# Project Charter — Aplicação de Indicadores Educacionais Brasileiros

## 1. Identificação do Projeto

**Nome do projeto:** Aplicação de Indicadores Educacionais Brasileiros

**Área:** Educação

**ODS Atendidas:** 
 - ODS4 - Educação de qualidade: provendo indicadores e métricas referentes à educação no país.
 - ODS5 - Igualdade de gênero: provendo indicadores e métricas de educação por gênero, evidenciando desigualdades.
 - ODS10 - Redução das desigualdades: provendo indicadores e métricas de educação por cor/raça, evidenciando desigualdades.

**Tecnologia principal:** Python e Streamlit

**Fontes de dados:** Fontes públicas, inicialmente com foco em arquivos e APIs do IBGE e INEP.

---

## 2. Problema de Negócio

É importante compreender as condições e desigualdades existentes na educação brasileira. Entretanto, os dados estão distribuídos em diferentes pesquisas e bases, o que pode dificultar sua consulta e comparação por pessoas sem conhecimento técnico. 

Essa dificuldade compromete a capacidade de identificar os problemas e desigualdades na educação, e dificulta a tomada de decisões baseada em dados. 

A aplicação poderá ajudar nessas situações facilitando o acesso e apoiando análises e decisões para questões como:

- Quais localidades apresentam indicadores mais preocupantes?
- Quais estados apresentam menores taxas de escolarização?
- Quais grupos apresentam maiores desigualdades nos indicadores educacionais?
- Onde podem ser necessárias ações específicas para melhorar determinados indicadores?

---

## 3. Objetivo Geral

Desenvolver uma aplicação interativa utilizando Streamlit para facilitar a consulta, visualização e comparação de indicadores relacionados à educação brasileira provenientes de fontes públicas.

---

## 4. Objetivos Específicos

- Coletar dados de fontes públicas relacionadas à educação;
- Integrar dados provenientes de APIs e outras fontes;
- Organizar e tratar os dados para análise;
- Disponibilizar os dados tratados e agregados;
- Facilitar a identificação de desigualdades e problemas relacionados à educação.
- Mostrar as notícias mais recentes ligadas à educação.

---

## 5. Escopo

- Coleta de dados por meio de APIs públicas;
- Coleta de dados por meio de web scraping em páginas estáticas, quando permitido;
- Coleta de dados por meio de web scraping em páginas dinâmicas, quando permitido;
- Tratamento e organização dos dados;
- Análise exploratória dos dados;
- Desenvolvimento de tabelas e visualizações;
- Desenvolvimento da aplicação utilizando Streamlit;

---

## 6. Metas

A principal meta do projeto é desenvolver uma aplicação funcional que organize e facilite o acesso a indicadores educacionais brasileiros.

O projeto deverá permitir que o usuário:

- Consulte indicadores educacionais;
- Visualize os indicadores por meio de gráficos e tabelas;
- Consulte informações sem precisar conhecer a estrutura técnica das APIs utilizadas.
- Consulte informações por API.

---

## 7. Indicadores de Sucesso

| **KPI**               | **Como medimos**                                          | **Meta** |
| --------------------- | --------------------------------------------------------- | -------- |
| Cobertura de fontes   | nº de fontes de notícias disponíveis no painel            | ≥ 3      |
| Extração de notícias em páginas dinâmicas | capacidade de carregar e processar notícias de páginas dinâmicas | sim |
| Cobertura de notícias | nº de notícias carregadas e processadas                   | ≥ 20    |
| Atualidade            | diferença entre a data da coleta e a notícia mais recente | ≤ 7 dias |
| Qualidade dos dados   | % de notícias com URL e manchete válidas                  | ≥ 95%    |
| Visualização          | nº de visualizações disponíveis para análise              | ≥ 3      |
| Interatividade        | nº de filtros disponíveis                                 | ≥ 2      |
| API funcional         | api em pleno funcionamento para consultas                 | sim      |

---

## 8. Stakeholders

- Gestores da área de educação;
- Organizações não governamentais (ONGs);

---

## 9. Entregável

O principal entregável do projeto será uma aplicação web interativa desenvolvida em **Python utilizando Streamlit**, capaz de consultar, organizar e visualizar indicadores educacionais provenientes de fontes públicas.