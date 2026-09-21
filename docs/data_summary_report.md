# Data Summary Report — Painel de Indicadores de Educação

## Fontes de dados
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

## Pipeline de coleta (Python puro)
`src/data_access.py`: `requests` 

Em caso de falha de rede, usa **cache** salvo previamente.

## Dicionário de dados (saída)
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


## Qualidade e observações
- Dados oficiais e públicos; sem dado pessoal (LGPD n/a).
- Período mais recente das tabelas 1187 e 1188: **2015**.

---

## Fonte 2 — WebScraping 

| Item | Valor |
|------|-------|
| Fonte | **Agência Brasil (EBC)** — `agenciabrasil.ebc.com.br` |
| Seção | Educação |
| Tipo | **Não estruturado** (HTML feito para leitores humanos) — não há API |
| Permissão | `robots.txt` **permite** as seções (verificado com `urllib.robotparser`) |
| Ritmo | `Crawl-delay: 10 s` — **respeitado** pelo coletor |
| Coleta | `src/data_scraping.py`, executado **à parte** (não pelo app) |
| Volume (19/09/2026) | **14 notícias** |
| Saída | `data/raw/noticias_{data_arquivo}.csv` · `noticias_{data_arquivo}.json` |

| Item | Valor |
|------|-------|
| Fonte | **G1 - Globo** — `g1.globo.com` |
| Seção | Educação |
| Tipo | **Não estruturado** (HTML feito para leitores humanos) — não há API |
| Permissão | `robots.txt` **permite** as seções (verificado com `urllib.robotparser`) |
| Ritmo | `Crawl-delay: 10 s` — **respeitado** pelo coletor |
| Coleta | `src/data_scraping.py`, executado **à parte** (não pelo app) |
| Volume (19/09/2026) | **8 notícias** |
| Saída | `data/raw/noticias_{data_arquivo}.csv` · `noticias_{data_arquivo}.json` |



### Dicionário de dados (`noticias_dd_mm_aaaa.csv`)
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `titulo` | texto | Manchete, já limpa (` `, espaços repetidos) |
| `data` | texto `dd/mm/aaaa hh:mm` | Data da matéria, extraída da página da notícia |
| `texto` | texto | Texto da matéria, extraída da página da notícia |
| `palavras` | inteiro | Tamanho do texto completo (insumo da contagem de palavras) |
| `url` | texto | Link absoluto da matéria |
| `fonte` | texto | Crédito exigido pela licença |

`robots.txt` → manchetes + links + matéria + data →
limpeza → CSV/JSON.

---

## Fonte 3 — Arquivo enviado pelo usuário

| Item | Valor |
|------|-------|
| Origem | CSV enviado pelo próprio usuário via `st.file_uploader` |
| Tipo | Estruturado (CSV) |
| Colunas obrigatórias | `manchete`, `url` |
| Validação | `src/news_transform.py :: ler_csv_enviado()` — devolve `(linhas, erro)` |
| Codificações aceitas | `utf-8-sig` → `utf-8` → `latin-1` |
| Onde vive | `st.session_state["noticias_enviadas"]` |