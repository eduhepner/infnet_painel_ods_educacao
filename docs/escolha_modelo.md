## 1. Tarefa

O modelo recebe uma **noticia** — texto livre, em português do Brasil, capturado por web scraping — e deve produzir uma versão reduzida, preservando as informações mais relevantes.
A tarefa é classificada como sumarização (*summarization*), uma tarefa específica de geração de texto (*text generation*).

## 2. Requisitos

| Requisito | Motivo |
|-----------|---------|
| Entende português do Brasil | Os relatos são escritos em português |
| Roda na CPU da máquina da API, sem nuvem | Execução local |
| Tempo de resposta | Usuário não espera |
| Baixa sem conta e sem token | O repositório é público: qualquer colega clona e roda |
| Licença que permite o uso | O projeto é aberto e pode ser reaproveitado |
| Performance | Precisa fazer o resumo de forma satisfatória |


## 3. Modelos

As fichas vêm de `python -m src.llm.ficha_modelo` (o Hub, antes de baixar):


| Modelo | Arquitetura | Tarefa no Hub | Licença | Gated | Parâmetros | Download |
|--------|-------------|---------------|---------|:-----:|-----------:|---------:|
| `recogna-nlp/ptt5-base-summ-xlsum` | encoder-decoder (T5) | sumarização | CC-BY-NC-SA 4.0 | não | 223 mi | 892 MB |
| `recogna-nlp/ptt5-base-summ-cstnews` | encoder-decoder (T5) | sumarização | MIT | não | 223 mi | 892 MB |
| `csebuetnlp/mT5_multilingual_XLSum` | encoder-decoder (mT5) | sumarização | não informada | não | não informado | 2,3 GB |
| `openai-community/gpt2-large` | decoder (GPT) | geração | MIT | não | 812 mi | 3,2 GB |
| `Qwen/Qwen2.5-0.5B-Instruct` | decoder (GPT) | geração | Apache 2.0 | não | 494 mi | 988 MB |
| `google/gemma-3-1b-it` | decoder (Gemma) | geração | Gemma | sim | 1.000 mi | 2 GB |
| `meta-llama/Llama-3.2-1B-Instruct` | decoder (Llama) | geração | Llama 3.2 | sim | 1.236 mi | 2,5 GB |
| `openai/gpt-oss-20b` | decoder (MoE) | geração | Apache 2.0 | não | 20.915 mi | 13,8 GB |

**Descartados pela ficha, sem baixar:**
- `google/gemma-3-1b-it` e `meta-llama/Llama-3.2-1B-Instruct` — **gated**: exigem conta no Hugging Face, aceite dos termos de licença e token de acesso. Não atendem ao requisito de acesso sem autorização prévia.
- `openai/gpt-oss-20b` — aproximadamente 20,9 bilhões de parâmetros e download de 13,8 GB. O custo computacional é elevado para o ambiente local.

**Mantidos apesar da tarefa declarada no Hub:**
- `openai-community/gpt2-large` e `Qwen/Qwen2.5-0.5B-Instruct` — são modelos de geração de texto, não especializados em sumarização. Podem ser testados mediante instruções de sumarização.
- O GPT-2 declara apenas inglês, e o Qwen também declara apenas inglês. A ausência de português nos metadados não comprova incapacidade de trabalhar com o idioma.

## 4. Testes

`python src.llm.llm_resumo_test.py`
10 notícias aleatórias são escolhidas, sendo então resumidas por cada modelo.
Detalhes em `.\src\llm\avaliacao_resumos.txt`

| Modelo                                             | Tempo médio por notícia | Mediana | Tempo máximo | Pesos na memória (MB) | Veredito                                                                                                                      |
| -------------------------------------------------- | ----------------------- | ------- | ------------ | --------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| recogna-nlp/ptt5-base-summ-xlsum (summarization)   | 5.69s                   | 5.68s   | 7.89s        | 891.6                 | Muito rápido e leve, mas apresenta resumos superficiais e alguns erros de interpretação                                       |
| recogna-nlp/ptt5-base-summ-cstnews (summarization) | 13.12s                  | 14.30s  | 19.91s       | 891.6                 | Tempo médio. É uma opção interessante para notícias, mas apresentou imprecisões                                               |
| csebuetnlp/mT5_multilingual_XLSum (summarization)  | 20.51s                  | 22.15s  | 30.93s       | 2.329,6               | Resumos coerentes em alguns casos, mas excessivamente curtos e com perda de informações importantes. Tempo médio pra longo    |
| openai-community/gpt2-large (gpt2)                 | 102.26s                 | 99.89s  | 126.88s      | 3.096,1               | Muito lento, com repetições excessivas e resultados inadequados para sumarização                                              |
| Qwen/Qwen2.5-0.5B-Instruct (qwen)                  | 56.88s                  | 61.23s  | 94.42s       | 1.976,1               | Lento. Produz resumos mais desenvolvidos, mas ainda apresenta imprecisões e repetições                                        |


## 5. Conclusão
O PTT5 XLSum apresenta o melhor desempenho computacional, enquanto o PTT5 CSTNews apresentou a qualidade mais satisfatória com tempo mais aceitável. Sendo assim, a princípio, foi escolhido o **`recogna-nlp/ptt5-base-summ-cstnews`**