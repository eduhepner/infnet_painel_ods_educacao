# Data Summary Report — Painel de Indicadores de Educação

## 1. Visão Geral e Ciclo de Vida dos Dados

Este documento descreve as fontes, o esquema, a qualidade e a integração dos dados utilizados no **Painel ODS - Educação Brasil**, cobrindo todo o ciclo de Ciência de Dados:

1. **Aquisição e Ingestão:** Coleta automatizada de indicadores oficiais via API do IBGE (SIDRA), extração de notícias educacionais via *web scraping* (estático e dinâmico) e ingestão de arquivos CSV enviados pelo usuário.
2. **Processamento e Padronização (`src/`):** Limpeza, tipagem, tratamento de codificações, normalização de colunas e filtragem/ordenação tabular com `pandas`.
3. **Disponibilização via API (`api/main.py`):** Exposição dos dados processados e modelos de sumarização por meio de endpoints RESTful em **FastAPI**, garantindo desacoplamento entre a camada de dados e a interface.
4. **Consumo Analítico e IA (`Streamlit` + `LLMs`):** Transformação dos dados em gráficos interativos (**Altair**), resumos automáticos de notícias (**PTT5**) e geração de insights sob demanda em linguagem natural por meio de um assistente conversacional aterrado nos dados (**Gemini 3.5 Flash-Lite**).

---
## 2. Fontes de dados

### Fonte 1 - API
| # | Fonte | Tipo | Endpoint | Objetivo de uso | Status |
|---|-------|------|----------|-----------------|--------|
| 1 | IBGE — Escolarização por sexo (tab. 7138, var. 10276) | Estruturado (JSON via API) | `/api/v3/agregados/7138/periodos/-1/variaveis/10276` | Indicador, UF, grupo de idade e Sexo | ✅ coletado ao vivo (2025) |
| 2 | IBGE — Escolarização por cor/raça (tab. 7139, var. 10276) | Estruturado (JSON via API) | `/api/v3/agregados/7139/periodos/-1/variaveis/10276` | Indicador, UF, grupo de idade e Cor/raça | ✅ coletado ao vivo (2025) |
| 3 | IBGE — Alfabetização por sexo (tab. 1187, var. 2513) | Estruturado (JSON via API) | `/api/v3/agregados/1187/periodos/-1/variaveis/2513` | Indicador, UF e Sexo | ✅ coletado ao vivo (2015) |
| 4 | IBGE — Alfabetização por cor/raça (tab. 1188, var. 2513) | Estruturado (JSON via API) | `/api/v3/agregados/1188/periodos/-1/variaveis/2513` | Indicador, UF e Cor/raça | ✅ coletado ao vivo (2015) |
| 5 | IBGE — Freequência escolar por sexo (tab. 7141, var. 10282) | Estruturado (JSON via API) | `/api/v3/agregados/7141/periodos/-1/variaveis/10282` | Indicador, UF, Faixa etária e Sexo | ✅ coletado ao vivo (2025) |
| 6 | IBGE — Frequência escolar por cor/raça (tab. 7142, var. 10282) | Estruturado (JSON via API) | `/api/v3/agregados/7142/periodos/-1/variaveis/10282` | Indicador, UF, Faixa etária e Cor/raça | ✅ coletado ao vivo (2025) |
| 7 | IBGE — Conclusão do ensino por sexo (tab. 10422, var. 4721) | Estruturado (JSON via API) | `/api/v3/agregados/10422/periodos/-1/variaveis/4721` | Indicador, UF, Grupo de idade e Sexo | ✅ coletado ao vivo (2025) |
| 8 | IBGE — Conclusão do ensino por cor/raça (tab. 9910, var. 4721) | Estruturado (JSON via API) | `/api/v3/agregados/9910/periodos/-1/variaveis/4721` | Indicador, UF, Grupo de idade e Cor/raça | ✅ coletado ao vivo (2025) |

#### Pipeline de coleta (Python puro)
* **Módulo:** `src/data_access.py` utilizando a biblioteca `requests` com metadados de timestamp (`coletado_em`).
* **Tolerância a falhas:** Em caso de indisponibilidade ou *timeout* da API externa do IBGE, o pipeline utiliza automaticamente o **cache local** armazenado em `data/processed/`, garantindo continuidade operacional.


#### Dicionário de dados (saída)
| Coluna                               | Tipo    | Descrição                                               |
| ------------------------------------ | ------- | ------------------------------------------------------- |
| `estado`                             | texto   | Nome do estado                                          |
| `sexo`                               | texto   | Sexo da população considerada                           |
| `grupo_idade`                        | texto   | Grupo de idade considerado no indicador                 |
| `taxa_escolarizacao`                 | decimal | Percentual de pessoas escolarizadas no grupo analisado  |
| `regiao`                             | texto   | Grande região do Brasil                                 |
| `cor_raca`                           | texto   | Categoria de cor ou raça da população                   |
| `taxa_alfabetizacao_15_anos_ou_mais` | decimal | Percentual de pessoas de 15 anos ou mais alfabetizadas  |
| `faixa_etaria_ideal_curso`           | texto   | Faixa etária considerada ideal para o curso frequentado |
| `taxa_ajustada_frequencia_escolar`   | decimal | Percentual ajustado de frequência escolar               |
| `taxa_conclusao_nivel_ensino`        | decimal | Percentual de conclusão do nível de ensino considerado  |


#### Qualidade, Governança e Observações
* **Conformidade LGPD:** Dados públicos, oficiais e agregados por UF/recorte demográfico; ausência total de dados pessoais sensíveis ou identificáveis (LGPD não aplicável).
* **Consistência Temporal:** As tabelas de alfabetização (1187 e 1188) refletem o período mais recente disponibilizado no agregado consultado (**2015**), enquanto os demais indicadores refletem a série atualizada (**2025**).

---

### Fonte 2 — WebScraping 

| Item | Valor |
|------|-------|
| Fonte | **Agência Brasil (EBC)** — `agenciabrasil.ebc.com.br` |
| Seção | Educação |
| Tipo | **Não estruturado** (HTML feito para leitores humanos) — sem API pública |
| Permissão | `robots.txt` **permite** as seções (verificado com `urllib.robotparser`) |
| Ritmo | `Crawl-delay: 10 s` — **respeitado** pelo coletor |
| Coleta | `src/data_scraping.py`, executado **à parte** (não pelo app) |
| Tipo de coleta | **Estática**, com BeautifulSoup |
| Volume (11/10/2026) | **14 notícias** |
| Saída | `data/raw/noticias.csv` · `data/raw/noticias.json` |

| Item | Valor |
|------|-------|
| Fonte | **G1 - Globo** — `g1.globo.com` |
| Seção | Educação |
| Tipo | **Não estruturado** (HTML feito para leitores humanos) — sem API pública |
| Permissão | `robots.txt` **permite** as seções (verificado com `urllib.robotparser`) |
| Ritmo | `Crawl-delay: 10 s` — **respeitado** pelo coletor |
| Coleta | `src/data_scraping.py`, executado **à parte** (não pelo app) |
| Tipo de coleta | **Dinâmica**, com Selenium, a partir de **rolagem da página**. |
| Volume (11/10/2026) | **31 notícias** |
| Saída | `data/raw/noticias.csv` · `data/raw/noticias.json` |



#### Dicionário de dados (`noticias.csv`)
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `titulo` | texto | Manchete, já limpa (` `, espaços repetidos) |
| `data` | texto `dd/mm/aaaa hh:mm` | Data da matéria, extraída da página da notícia |
| `texto` | texto | Texto da matéria, extraída da página da notícia |
| `palavras` | inteiro | Tamanho do texto completo (insumo da contagem de palavras) |
| `url` | texto | Link absoluto da matéria |
| `fonte` | texto | Crédito exigido pela licença |


#### Derivado - contagem e nuvem de palavras
`src/news_transform.py` lê `data/processed/texto.txt` e produz a frequência de termos.
Com isso, é feita a nuvem de palavras através das bibliotecas `sklearn` e `wordcloud`.

#### Derivado - resumo
A rota da API `/noticias/resumir` chama `src/resumidor`, que lê `data/raw/noticias.csv` 
e encontra a notícia, produzindo um resumo através da LLM `recogna-nlp/ptt5-base-summ-cstnews`
É retornado um `json` conendo o resumo da notícia.

> **Fluxo de transformação textual:** `robots.txt` → Extração (HTML estático/dinâmico) → Higienização → `data/raw/noticias.csv` → Processamento NLP (`src/news_transform.py`) → Nuvem de palavras (`sklearn` + `wordcloud`) e Sumarização via LLM (`src/resumidor.py`).

---

### Fonte 3 — Arquivo enviado pelo usuário

| Item | Valor |
|------|-------|
| Origem | CSV enviado pelo próprio usuário via `st.file_uploader` |
| Tipo | Estruturado (CSV) |
| Colunas obrigatórias | `manchete`, `url` |
| Validação | `src/news_transform.py :: ler_csv_enviado()` — devolve `(linhas, erro)` |
| Codificações aceitas | `utf-8-sig` → `utf-8` → `latin-1` |
| Onde vive | `st.session_state["noticias_enviadas"]` |

---

### Fonte 4 — API

| Item | Valor |
|------|-------|
| Código | `api/main.py` — **FastAPI** |
| Rota | `/noticia/enviar` |
| Execução | Serviço independente: `uvicorn api.main:app --reload` |
| Validação | Feito pela biblioteca `pydantic`, onde é definida a classe das notícias (`class Noticia`), em `api/model/model.py`|
| Formato | Lista de dicionários com mínimo de 1 elemento |
| Colunas obrigatórias | `fonte`, `manchete`, `url` |
| Salvo em | `data/cache/noticias_enviadas.csv` |
| Documentação | Gerada do próprio código: `/docs` (interativa) e `/redoc`; o esquema em `/openapi.json` |

---

### Fonte 5 — Modelos de IA / LLMs Integrados

| Modelo / Componente | Módulo | Função no Pipeline | Entrada de Dados | Saída Gerada |
| :--- | :--- | :--- | :--- | :--- |
| **PTT5 (`recogna-nlp/ptt5-base-summ-cstnews`)** | `src/resumidor.py` (via `GET /noticias/resumir`) | Sumarização automática de notícias educacionais em português | Texto completo da notícia localizada em `data/raw/noticias.csv` | JSON estruturado (`class Resumo`) com síntese da matéria |
| **Gemini 3.5 Flash-Lite (`google-genai`)** | Páginas do painel Streamlit (``/pages/alfabetizacao.py``, ``/pages/conclusao.py``, ``/pages/escolarizacao.py``, ``/pages/frequencia.py``) | Assistente conversacional analítico com memória de curto prazo | DataFrames tratados (`df_sexo` e `df_cor`) obtidos da API e serializados em CSV no *System Prompt* | Respostas analíticas, rankings, comparações e insights em português |

---

## 3. Integração e Saída dos Dados

### Arquitetura de Integração (De Dados Brutos a Insights)

```text
[IBGE API] ──► src/data_access.py ──► data/processed/ ──┐
                                                         ├──► FastAPI (api/main.py) ──► Streamlit UI
[EBC / G1] ──► src/data_scraping.py ─► data/raw/ ────────┤         │                        │
                                                         │         ▼                        ▼
[CSV User] ──► st.file_uploader ─────────────────────────┘   PTT5 (Resumos)       Gráficos Altair +
                                                                                  Nuvem de Palavras +
                                                                                  Exportação CSV +
                                                                                  Gemini Chat (Insights)
```

### Saída 1 — API RESTful (`api/main.py` — FastAPI)

| Item | Valor |
|------|-------|
| Código | `api/main.py` — **FastAPI** |
| Execução | **à parte**, na máquina de quem a usa: `uvicorn api.main:app --reload` (ambiente de `requirements-api.txt`) |
| De onde lê | dos **mesmos** arquivos de `data/processed/`, com as **mesmas** funções de `src/` |
| Formato | `JSON`. |
| Documentação | gerada do próprio código: `/docs` (interativa) e `/redoc`; o esquema em `/openapi.json` |


#### Rotas (GET)

| Rota | Parâmetros | Responde |
|------|------------|----------|
| `/` | — | o que a API serve e onde está a documentação |
| `/docs` | — | documentação da API |
| `/alfabetizacao` | - `tipo` (obrigatório): `cor`, `sexo`<br>- `regiao` (opcional): lista contendo um ou mais de `Norte`, `Nordeste`, `Centro-Oeste`, `Sudeste`, `Sul`<br>- `minimo` (opcional): valor mínimo da `taxa de alfabetização` retornada | dados de alfabetização |
| `/conclusao` | - `tipo` (obrigatório) : `cor`, `sexo`<br>- `regiao` (opcional): lista contendo um ou mais de `Norte`, `Nordeste`, `Centro-Oeste`, `Sudeste`, `Sul`<br>- `minimo` (opcional): valor mínimo da `taxa de conclusão` retornada | dados de conclusão do ensino |
| `/escolarizacao` | - `tipo` (obrigatório) : `cor`, `sexo`<br>- `regiao` (opcional): lista contendo um ou mais de `Norte`, `Nordeste`, `Centro-Oeste`, `Sudeste`, `Sul`<br>- `minimo` (opcional): valor mínimo da `taxa de escolarização` retornada | dados de escolarização |
| `/frequencia` | - `tipo` (obrigatório) : `cor`, `sexo`<br>- `regiao` (opcional): lista contendo um ou mais de `Norte`, `Nordeste`, `Centro-Oeste`, `Sudeste`, `Sul`<br>- `minimo` (opcional): valor mínimo da `taxa de frequência` retornada | dados de frequência escolar |
| `/noticias` | - `quantidade` (opcional): quantidade máxima de notícias retornadas (int > 1) | as notícias da última coleta, data da coleta e fontes |
| `/noticias/fontes` | — | apenas as fontes das notícias |
| `/noticias/resumir` | - `manchete` (obrigatório): manchete da notícia a ser resumida (str > 1) | resumo da notícia gerado pelo modelo PTT5 |

#### Rotas (POST)

| Rota | Parâmetros | Responde |
|------|------------|----------|
| `/noticias/enviar` | - `fonte` (opcional) : Nome da fonte de publicação da notícia. Pode receber um `string` ou `None`.<br> - `manchete` (obrigatório) : Título da notícia. Deve conter pelo menos um caractere<br>- `data` (opcional): Data ou data e horário de publicação da notícia. Recebe `date` ou `datetime`.<br>- `palavras` (opcional): Quantidade de palavras do texto da notícia. Quando informado, deve ser um `número inteiro` igual ou superior a 50 (`ge=50`).<br> - `url` (obrigatório) : Deve corresponder a uma URL válida.<br>- `texto` (opcional): Conteúdo textual completo da notícia. Pode receber `string` ou `None`. | Envio de notícias. |

---

### Saída 2 — Dashboard Interativo e Exportação (`Streamlit`)

| Componente de Saída | Biblioteca | Descrição |
| :--- | :--- | :--- |
| **Gráficos Comparativos** | `Altair` (`src/graphics.py`) | Gráficos interativos por Unidade Federativa comparando recortes de **Sexo** e **Cor/Raça** para cada indicador educacional |
| **Métricas Dinâmicas** | `st.metric` | Contadores dinâmicos de regiões e estados ativos conforme os filtros aplicados na barra lateral |
| **Tabelas e Download** | `st.dataframe` / `st.download_button` | Exibição tabular sob demanda com opção de exportação direta dos dados filtrados em formato **CSV** (`painel_ods_filtrado.csv`) |
| **Análise Textual de Notícias** | `sklearn` + `wordcloud` | Nuvem de palavras e frequência dos termos mais recorrentes nas matérias coletadas sobre educação |
| **Diagnóstico e Prioridade Regional (IA)** | `Gemini` (`Pydantic JSON`) + `Altair` | Matriz de criticidade educacional (0–100) e plano de ação por região gerados automaticamente a partir do cruzamento dos 4 indicadores |

---

### Saída 3 — Assistente Conversacional com IA (`Chat`)

| Item | Valor |
| :--- | :--- |
| Execução | **Diretamente na página** de cada métrica (*Alfabetização*, *Conclusão*, *Escolarização* e *Frequência*), ao clicar no botão flutuante **"💬 Assistente de Dados"** (`st.popover`), e na página consolidada de **Visão Geral & Governança (ESG)** |
| De onde lê | Dos **mesmos** DataFrames tratados provenientes da API (`df_sexo` e `df_cor`), serializados dinamicamente em formato **CSV** nas instruções de sistema (*in-context learning*) |
| Engenharia de Prompt e Memória | Prompt restritivo (*grounding*) que impede o uso de dados externos, valida colunas de recorte etário (`Grupo de idade` / `Faixa etária ideal`), opera com `temperature=0.1` e mantém **memória conversacional isolada por página** (`st.session_state`) com janela deslizante das últimas interações |
| Formato de saída | Linguagem natural em português (rankings estaduais, comparações demográficas, identificação de desigualdades e suporte à tomada de decisão) |
| Modelo | **Gemini 3.5 Flash-Lite**, via API (`google-genai`) |