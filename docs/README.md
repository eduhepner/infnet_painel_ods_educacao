# Painel ODS - Educação Brasil

## SOBRE

Este aplicativo foi desenvolvido como parte da disciplina de **Projeto de Bloco**, do curso de **Ciência de Dados** da Faculdade Infnet.

## COMO UTILIZAR

#### 1. AMBIENTE

Para criar um ambiente virtual e isolar as dependências do projeto:

```bash
python -m venv .venv
```

Para ativar o ambiente virtual no PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

#### 2. COLETA DE DADOS

**Instalar as dependências da coleta:**

```bash
pip install -r requirements-coleta.txt
```

**Executar a coleta:**

```bash
python .\src\data_scraping.py
```

**Etapas da coleta:**

1. Consulta as permissões de acesso no `robots.txt` dos dois sites.
2. Acessa o G1 utilizando Selenium e carrega os links das notícias.
3. Acessa a Agência Brasil utilizando Requests e BeautifulSoup para extrair os links.
4. Percorre os links encontrados em cada site.
5. Acessa individualmente cada notícia.
6. Extrai título, data, texto, quantidade de palavras, URL e fonte.
7. Salva os resultados em `data/raw/noticias.csv`.
8. Salva os metadados em `data/raw/noticias.json`.

**Observações:**

- O intervalo entre requisições é de 10 segundos, salvo se o `robots.txt` determinar outro intervalo.
- O scraping pode demorar alguns minutos, dependendo da quantidade de notícias.
- O Chrome e o ChromeDriver precisam estar disponíveis e configurados para que a coleta dinâmica do G1 funcione.
- O arquivo `noticias.csv` é sobrescrito a cada execução, não sendo um histórico acumulativo.

#### 3. API

**Instalar as dependências da API:**

```bash
pip install -r requirements-api.txt
```

**Executar a API:**

```bash
uvicorn api.main:app --reload
```

A documentação interativa da API pode ser acessada em:

[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

#### 4. MODELO

Para baixar o modelo usado:

```bash
python .\src\llm\llm_download.py
```

#### 5. APLICATIVO

Para executar o aplicativo Streamlit:

```bash
streamlit run app.py
```


## INFORMAÇÕES E REQUISITOS TÉCNICOS

#### MODELO
- Número de parâmetros: 0,2 bilhão (200M)
- Tipo dos tensores: F32 (float32)
- Tamanho dos pesos: Aproximadamente 892 MB
- Comprimento máximo de entrada: 512 tokens
- Tamanho em disco: 1.66 GB
- Tempo de carga na primeira chamada: 22.46s

#### ESPECIFICAÇÕES
**Todos os testes e tempos foram cálculados em**:
- CPU:	    AMD Ryzen 5 5600X 6-Core Processor 3.70 GHz
- Memória RAM:      32 GB

**Requisitos mínimos estimados**:
- CPU: x86-64 moderno, 4 núcleos ou mais
- Precisão: float32 (FP32)
- Memória RAM:	8 GB no mínimo; 16 GB recomendados
- Armazenamento:	Pelo menos 2 GB livres para o modelo e arquivos auxiliares