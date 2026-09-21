import json
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests

BASE = Path(__file__).resolve().parent.parent
RAW = BASE / "data" / "raw"
CACHE = BASE / "data" / "cache"

TIME_LIMIT = 30

regioes = {
    "Acre": "Norte",
    "Alagoas": "Nordeste",
    "Amapá": "Norte",
    "Amazonas": "Norte",
    "Bahia": "Nordeste",
    "Ceará": "Nordeste",
    "Distrito Federal": "Centro-Oeste",
    "Espírito Santo": "Sudeste",
    "Goiás": "Centro-Oeste",
    "Maranhão": "Nordeste",
    "Mato Grosso": "Centro-Oeste",
    "Mato Grosso do Sul": "Centro-Oeste",
    "Minas Gerais": "Sudeste",
    "Pará": "Norte",
    "Paraíba": "Nordeste",
    "Paraná": "Sul",
    "Pernambuco": "Nordeste",
    "Piauí": "Nordeste",
    "Rio de Janeiro": "Sudeste",
    "Rio Grande do Norte": "Nordeste",
    "Rio Grande do Sul": "Sul",
    "Rondônia": "Norte",
    "Roraima": "Norte",
    "Santa Catarina": "Sul",
    "São Paulo": "Sudeste",
    "Sergipe": "Nordeste",
    "Tocantins": "Norte",
}


def verificar_metadados(agregado):
    url = f"https://servicodados.ibge.gov.br/api/v3/agregados/{agregado}/metadados"
    try:
        response = requests.get(url, timeout=TIME_LIMIT)
        response.raise_for_status()
        metadados = response.json()
        return metadados

    except requests.exceptions.Timeout:
        print("Tempo limite excedido ao consultar a API.")
        return None


def salvar_cache(df, nome, agregado):
    CACHE.mkdir(parents=True, exist_ok=True)
    df.to_csv(CACHE / nome, index=False, encoding="utf-8")

    metadados = {
        "coletado_em": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "agregado": agregado,
    }

    nome_json = Path(nome).with_suffix(".json")
    with open(CACHE / nome_json, "w", encoding="utf-8") as arquivo:
        json.dump(metadados, arquivo, ensure_ascii=False, indent=4)


def ler_cache(nome):
    caminho = CACHE / nome

    if not caminho.exists():
        raise FileNotFoundError(f"Cache não encontrado: {caminho}")

    df = pd.read_csv(caminho)

    nome_json = Path(nome).with_suffix(".json")
    caminho_json = CACHE / nome_json

    with open(caminho_json, encoding="utf-8") as arquivo:
        metadados = json.load(arquivo)

    coletado_em = metadados["coletado_em"]

    return df, f"API indisponível - cache local coletado em {coletado_em}"


# escolarização por sexo
def buscar_taxa_escolarizacao_sexo():
    agregado = 7138
    metadados = verificar_metadados(agregado)

    if metadados is None:
        df, msg = ler_cache("escolarizacao_sexo.csv")

    else:
        ano = metadados["periodicidade"]["fim"]
        variavel = metadados["variaveis"][0]["id"]

        params = {
            "localidades": "N3[all]",
            "classificacao": "2[6794,4,5]|58[95253,41126,99749,47813,31615,2792,100052,108866]",
        }

        url = f"https://servicodados.ibge.gov.br/api/v3/agregados/{agregado}/periodos/{ano}/variaveis/{variavel}"
        resp = requests.get(url, params=params, timeout=TIME_LIMIT)
        resp.raise_for_status()
        dados = resp.json()

        linhas = []

        for resultado in dados[0]["resultados"]:
            # ------------------------------
            # Sexo
            # ------------------------------
            sexo = resultado["classificacoes"][0]["categoria"]

            # ------------------------------
            # Grupo de idade
            # ------------------------------
            grupo_idade = resultado["classificacoes"][1]["categoria"]

            # ------------------------------
            # Localidade
            # ------------------------------
            for serie in resultado["series"]:
                estado = serie["localidade"]["nome"]

                # ------------------------------
                # Valor do último ano
                # ------------------------------
                valor = serie["serie"][str(ano)]

                # ------------------------------
                # Montando as linhas
                # ------------------------------
                linhas.append(
                    {
                        "Estado": estado,
                        "Sexo": list(sexo.values())[0],
                        "Grupo de idade": list(grupo_idade.values())[0],
                        "Taxa de escolarização (%)": valor,
                    }
                )
        # ==========================================
        # 4. DATAFRAME
        # ==========================================
        df = pd.DataFrame(linhas)

        # ==========================================
        # 5. CONVERSÃO DO VALOR
        # ==========================================
        df["Taxa de escolarização (%)"] = pd.to_numeric(
            df["Taxa de escolarização (%)"], errors="coerce"
        )

        # ==========================================
        # 6. ORDENAÇÃO
        # ==========================================
        df = df.sort_values(by=["Estado", "Sexo"]).reset_index(drop=True)

        # ==========================================
        # 7. ADICIONANDO REGIÃO
        # ==========================================
        df["Região"] = df["Estado"].map(regioes)

        df = df[
            ["Região", "Estado", "Sexo", "Grupo de idade", "Taxa de escolarização (%)"]
        ]

        salvar_cache(df, "escolarizacao_sexo.csv", agregado)
        msg = "API do IBGE (ao vivo)"
    return df, msg


# escolarização por Cor/raça
def buscar_taxa_escolarizacao_cor():
    agregado = 7139
    metadados = verificar_metadados(agregado)
    if metadados is None:
        df, msg = ler_cache("escolarizacao_cor.csv")

    else:
        ano = metadados["periodicidade"]["fim"]
        variavel = metadados["variaveis"][0]["id"]

        params = {
            "localidades": "N3[all]",
            "classificacao": "86[95251,2776,119525]|58[95253,41126,99749,47813,31615,2792,100052,108866]",
        }

        url = f"https://servicodados.ibge.gov.br/api/v3/agregados/{agregado}/periodos/{ano}/variaveis/{variavel}"
        resp = requests.get(url, params=params, timeout=TIME_LIMIT)
        resp.raise_for_status()
        dados = resp.json()

        linhas = []

        for resultado in dados[0]["resultados"]:
            # ------------------------------
            # Cor
            # ------------------------------
            cor = resultado["classificacoes"][0]["categoria"]

            # ------------------------------
            # Grupo de idade
            # ------------------------------
            grupo_idade = resultado["classificacoes"][1]["categoria"]

            # ------------------------------
            # Localidade
            # ------------------------------
            for serie in resultado["series"]:
                estado = serie["localidade"]["nome"]

                # ------------------------------
                # Valor do último ano
                # ------------------------------
                valor = serie["serie"][str(ano)]

                # ------------------------------
                # Montando as linhas
                # ------------------------------
                linhas.append(
                    {
                        "Estado": estado,
                        "Cor/raça": list(cor.values())[0],
                        "Grupo de idade": list(grupo_idade.values())[0],
                        "Taxa de escolarização (%)": valor,
                    }
                )
        # ==========================================
        # 4. DATAFRAME
        # ==========================================
        df = pd.DataFrame(linhas)

        # ==========================================
        # 5. CONVERSÃO DO VALOR
        # ==========================================
        df["Taxa de escolarização (%)"] = pd.to_numeric(
            df["Taxa de escolarização (%)"], errors="coerce"
        )

        # ==========================================
        # 6. ORDENAÇÃO
        # ==========================================
        df = df.sort_values(by=["Estado", "Cor/raça"]).reset_index(drop=True)

        # ==========================================
        # 7. ADICIONANDO REGIÃO
        # ==========================================
        df["Região"] = df["Estado"].map(regioes)

        df = df[
            [
                "Região",
                "Estado",
                "Cor/raça",
                "Grupo de idade",
                "Taxa de escolarização (%)",
            ]
        ]

        salvar_cache(df, "escolarizacao_cor.csv", agregado)
        msg = "API do IBGE (ao vivo)"
    return df, msg


# alfabetização por sexo
def buscar_taxa_alfabetizacao_sexo():
    agregado = 1187
    metadados = verificar_metadados(agregado)

    if metadados is None:
        df, msg = ler_cache("alfabetizacao_sexo.csv")

    else:
        ano = metadados["periodicidade"]["fim"]
        variavel = metadados["variaveis"][0]["id"]

        params = {"localidades": "N3[all]", "classificacao": "2[6794,4,5]"}

        url = f"https://servicodados.ibge.gov.br/api/v3/agregados/{agregado}/periodos/{ano}/variaveis/{variavel}"
        resp = requests.get(url, params=params, timeout=TIME_LIMIT)
        resp.raise_for_status()
        dados = resp.json()

        linhas = []

        for resultado in dados[0]["resultados"]:
            # ------------------------------
            # Sexo
            # ------------------------------
            sexo = resultado["classificacoes"][0]["categoria"]

            # ------------------------------
            # Localidade
            # ------------------------------
            for serie in resultado["series"]:
                estado = serie["localidade"]["nome"]

                # ------------------------------
                # Valor do último ano
                # ------------------------------
                valor = serie["serie"][str(ano)]

                # ------------------------------
                # Montando as linhas
                # ------------------------------
                linhas.append(
                    {
                        "Estado": estado,
                        "Sexo": list(sexo.values())[0],
                        "Taxa de alfabetização 15+ anos (%)": valor,
                    }
                )
        # ==========================================
        # 4. DATAFRAME
        # ==========================================
        df = pd.DataFrame(linhas)

        # ==========================================
        # 5. CONVERSÃO DO VALOR
        # ==========================================
        df["Taxa de alfabetização 15+ anos (%)"] = pd.to_numeric(
            df["Taxa de alfabetização 15+ anos (%)"],
            errors="coerce",
        )

        # ==========================================
        # 6. ORDENAÇÃO
        # ==========================================
        df = df.sort_values(by=["Estado", "Sexo"]).reset_index(drop=True)

        # ==========================================
        # 7. ADICIONANDO REGIÃO
        # ==========================================
        df["Região"] = df["Estado"].map(regioes)

        df = df[
            [
                "Região",
                "Estado",
                "Sexo",
                "Taxa de alfabetização 15+ anos (%)",
            ]
        ]
        salvar_cache(df, "alfabetizacao_sexo.csv", agregado)
        msg = "API do IBGE (ao vivo)"
    return df, msg


# alfabetização por Cor/raça
def buscar_taxa_alfabetizacao_cor():
    agregado = 1188
    metadados = verificar_metadados(agregado)
    if metadados is None:
        df, msg = ler_cache("alfabetizacao_cor.csv")

    else:
        ano = metadados["periodicidade"]["fim"]
        variavel = metadados["variaveis"][0]["id"]

        params = {"localidades": "N3[all]", "classificacao": "86[95251,2776,119525]"}

        url = f"https://servicodados.ibge.gov.br/api/v3/agregados/{agregado}/periodos/{ano}/variaveis/{variavel}"
        resp = requests.get(url, params=params, timeout=TIME_LIMIT)
        resp.raise_for_status()
        dados = resp.json()

        linhas = []

        for resultado in dados[0]["resultados"]:
            # ------------------------------
            # Sexo
            # ------------------------------
            cor = resultado["classificacoes"][0]["categoria"]

            # ------------------------------
            # Localidade
            # ------------------------------
            for serie in resultado["series"]:
                estado = serie["localidade"]["nome"]

                # ------------------------------
                # Valor do último ano
                # ------------------------------
                valor = serie["serie"][str(ano)]

                # ------------------------------
                # Montando as linhas
                # ------------------------------
                linhas.append(
                    {
                        "Estado": estado,
                        "Cor/raça": list(cor.values())[0],
                        "Taxa de alfabetização 15+ anos (%)": valor,
                    }
                )
        # ==========================================
        # 4. DATAFRAME
        # ==========================================
        df = pd.DataFrame(linhas)

        # ==========================================
        # 5. CONVERSÃO DO VALOR
        # ==========================================
        df["Taxa de alfabetização 15+ anos (%)"] = pd.to_numeric(
            df["Taxa de alfabetização 15+ anos (%)"],
            errors="coerce",
        )

        # ==========================================
        # 6. ORDENAÇÃO
        # ==========================================
        df = df.sort_values(by=["Estado", "Cor/raça"]).reset_index(drop=True)

        # ==========================================
        # 7. ADICIONANDO REGIÃO
        # ==========================================
        df["Região"] = df["Estado"].map(regioes)

        df = df[
            [
                "Região",
                "Estado",
                "Cor/raça",
                "Taxa de alfabetização 15+ anos (%)",
            ]
        ]
        salvar_cache(df, "alfabetizacao_cor.csv", agregado)
        msg = "API do IBGE (ao vivo)"
    return df, msg


# frequencia por sexo
def buscar_taxa_frequencia_sexo():
    agregado = 7141
    metadados = verificar_metadados(agregado)
    if metadados is None:
        df, msg = ler_cache("frequencia_sexo.csv")

    else:
        ano = metadados["periodicidade"]["fim"]
        variavel = metadados["variaveis"][0]["id"]

        params = {
            "localidades": "N3[all]",
            "classificacao": "2[6794,4,5]|871[47815,47816,47817,47818,47819]",
        }

        url = f"https://servicodados.ibge.gov.br/api/v3/agregados/{agregado}/periodos/{ano}/variaveis/{variavel}"
        resp = requests.get(url, params=params, timeout=TIME_LIMIT)
        resp.raise_for_status()
        dados = resp.json()

        linhas = []

        for resultado in dados[0]["resultados"]:
            # ------------------------------
            # Sexo
            # ------------------------------
            sexo = resultado["classificacoes"][0]["categoria"]

            # ------------------------------
            # Grupo de idade
            # ------------------------------
            faixa_etaria = resultado["classificacoes"][1]["categoria"]

            # ------------------------------
            # Localidade
            # ------------------------------
            for serie in resultado["series"]:
                estado = serie["localidade"]["nome"]

                # ------------------------------
                # Valor do último ano
                # ------------------------------
                valor = serie["serie"][str(ano)]

                # ------------------------------
                # Montando as linhas
                # ------------------------------
                linhas.append(
                    {
                        "Estado": estado,
                        "Sexo": list(sexo.values())[0],
                        "Faixa etária ideal por curso frequentado": list(
                            faixa_etaria.values()
                        )[0],
                        "Taxa ajustada de frequência escolar (%)": valor,
                    }
                )
        # ==========================================
        # 4. DATAFRAME
        # ==========================================
        df = pd.DataFrame(linhas)

        # ==========================================
        # 5. CONVERSÃO DO VALOR
        # ==========================================
        df["Taxa ajustada de frequência escolar (%)"] = pd.to_numeric(
            df["Taxa ajustada de frequência escolar (%)"], errors="coerce"
        )

        # ==========================================
        # 6. ORDENAÇÃO
        # ==========================================
        df = df.sort_values(by=["Estado", "Sexo"]).reset_index(drop=True)

        # ==========================================
        # 7. ADICIONANDO REGIÃO
        # ==========================================
        df["Região"] = df["Estado"].map(regioes)

        df = df[
            [
                "Região",
                "Estado",
                "Sexo",
                "Faixa etária ideal por curso frequentado",
                "Taxa ajustada de frequência escolar (%)",
            ]
        ]

        salvar_cache(df, "frequencia_sexo.csv", agregado)
        msg = "API do IBGE (ao vivo)"
    return df, msg


# frequencia por Cor/raça
def buscar_taxa_frequencia_cor():
    agregado = 7142
    metadados = verificar_metadados(agregado)
    if metadados is None:
        df, msg = ler_cache("frequencia_cor.csv")

    else:
        ano = metadados["periodicidade"]["fim"]
        variavel = metadados["variaveis"][0]["id"]

        params = {
            "localidades": "N3[all]",
            "classificacao": "86[95251,2776,119525]|871[47815,47816,47817,47818,47819]",
        }

        url = f"https://servicodados.ibge.gov.br/api/v3/agregados/{agregado}/periodos/{ano}/variaveis/{variavel}"
        resp = requests.get(url, params=params, timeout=TIME_LIMIT)
        resp.raise_for_status()
        dados = resp.json()

        linhas = []

        for resultado in dados[0]["resultados"]:
            # ------------------------------
            # Cor
            # ------------------------------
            cor = resultado["classificacoes"][0]["categoria"]

            # ------------------------------
            # Grupo de idade
            # ------------------------------
            faixa_etaria = resultado["classificacoes"][1]["categoria"]

            # ------------------------------
            # Localidade
            # ------------------------------
            for serie in resultado["series"]:
                estado = serie["localidade"]["nome"]

                # ------------------------------
                # Valor do último ano
                # ------------------------------
                valor = serie["serie"][str(ano)]

                # ------------------------------
                # Montando as linhas
                # ------------------------------
                linhas.append(
                    {
                        "Estado": estado,
                        "Cor/raça": list(cor.values())[0],
                        "Faixa etária ideal por curso frequentado": list(
                            faixa_etaria.values()
                        )[0],
                        "Taxa ajustada de frequência escolar (%)": valor,
                    }
                )
        # ==========================================
        # 4. DATAFRAME
        # ==========================================
        df = pd.DataFrame(linhas)

        # ==========================================
        # 5. CONVERSÃO DO VALOR
        # ==========================================
        df["Taxa ajustada de frequência escolar (%)"] = pd.to_numeric(
            df["Taxa ajustada de frequência escolar (%)"], errors="coerce"
        )

        # ==========================================
        # 6. ORDENAÇÃO
        # ==========================================
        df = df.sort_values(by=["Estado", "Cor/raça"]).reset_index(drop=True)

        # ==========================================
        # 7. ADICIONANDO REGIÃO
        # ==========================================
        df["Região"] = df["Estado"].map(regioes)

        df = df[
            [
                "Região",
                "Estado",
                "Cor/raça",
                "Faixa etária ideal por curso frequentado",
                "Taxa ajustada de frequência escolar (%)",
            ]
        ]
        salvar_cache(df, "frequencia_cor.csv", agregado)
        msg = "API do IBGE (ao vivo)"
    return df, msg


# conclusao por sexo
def buscar_taxa_conclusao_sexo():
    agregado = 10422
    metadados = verificar_metadados(agregado)
    if metadados is None:
        df, msg = ler_cache("conclusao_sexo.csv")

    else:
        ano = metadados["periodicidade"]["fim"]
        variavel = metadados["variaveis"][0]["id"]

        params = {
            "localidades": "N3[all]",
            "classificacao": "2[6794,4,5]|582[59995,59996,59997]",
        }

        url = f"https://servicodados.ibge.gov.br/api/v3/agregados/{agregado}/periodos/{ano}/variaveis/{variavel}"
        resp = requests.get(url, params=params, timeout=TIME_LIMIT)
        resp.raise_for_status()
        dados = resp.json()

        linhas = []

        for resultado in dados[0]["resultados"]:
            # ------------------------------
            # Sexo
            # ------------------------------
            sexo = resultado["classificacoes"][0]["categoria"]

            # ------------------------------
            # Grupo de idade
            # ------------------------------
            grupo_idade = resultado["classificacoes"][1]["categoria"]

            # ------------------------------
            # Localidade
            # ------------------------------
            for serie in resultado["series"]:
                estado = serie["localidade"]["nome"]

                # ------------------------------
                # Valor do último ano
                # ------------------------------
                valor = serie["serie"][str(ano)]

                # ------------------------------
                # Montando as linhas
                # ------------------------------
                linhas.append(
                    {
                        "Estado": estado,
                        "Sexo": list(sexo.values())[0],
                        "Grupo de idade": list(grupo_idade.values())[0],
                        "Taxas de conclusão de nível de ensino (%)": valor,
                    }
                )
        # ==========================================
        # 4. DATAFRAME
        # ==========================================
        df = pd.DataFrame(linhas)

        # ==========================================
        # 5. CONVERSÃO DO VALOR
        # ==========================================
        df["Taxas de conclusão de nível de ensino (%)"] = pd.to_numeric(
            df["Taxas de conclusão de nível de ensino (%)"], errors="coerce"
        )

        # ==========================================
        # 6. ORDENAÇÃO
        # ==========================================
        df = df.sort_values(by=["Estado", "Sexo"]).reset_index(drop=True)

        # ==========================================
        # 7. ADICIONANDO REGIÃO
        # ==========================================
        df["Região"] = df["Estado"].map(regioes)

        df = df[
            [
                "Região",
                "Estado",
                "Sexo",
                "Grupo de idade",
                "Taxas de conclusão de nível de ensino (%)",
            ]
        ]
        salvar_cache(df, "conclusao_sexo.csv", agregado)
        msg = "API do IBGE (ao vivo)"
    return df, msg


# conclusao por Cor/raça
def buscar_taxa_conclusao_cor():
    agregado = 9910
    metadados = verificar_metadados(agregado)
    if metadados is None:
        df, msg = ler_cache("conclusao_cor.csv")

    else:
        ano = metadados["periodicidade"]["fim"]
        variavel = metadados["variaveis"][0]["id"]

        params = {
            "localidades": "N3[all]",
            "classificacao": "86[95251,2776,2777,2779]|582[59995,59996,59997]",
        }

        url = f"https://servicodados.ibge.gov.br/api/v3/agregados/{agregado}/periodos/{ano}/variaveis/{variavel}"
        resp = requests.get(url, params=params, timeout=TIME_LIMIT)
        resp.raise_for_status()
        dados = resp.json()

        linhas = []

        for resultado in dados[0]["resultados"]:
            # ------------------------------
            # Cor
            # ------------------------------
            cor = resultado["classificacoes"][0]["categoria"]

            # ------------------------------
            # Grupo de idade
            # ------------------------------
            grupo_idade = resultado["classificacoes"][1]["categoria"]

            # ------------------------------
            # Localidade
            # ------------------------------
            for serie in resultado["series"]:
                estado = serie["localidade"]["nome"]

                # ------------------------------
                # Valor do último ano
                # ------------------------------
                valor = serie["serie"][str(ano)]

                # ------------------------------
                # Montando as linhas
                # ------------------------------
                linhas.append(
                    {
                        "Estado": estado,
                        "Cor/raça": list(cor.values())[0],
                        "Grupo de idade": list(grupo_idade.values())[0],
                        "Taxas de conclusão de nível de ensino (%)": valor,
                    }
                )
        # ==========================================
        # 4. DATAFRAME
        # ==========================================
        df = pd.DataFrame(linhas)

        # ==========================================
        # 5. CONVERSÃO DO VALOR
        # ==========================================
        df["Taxas de conclusão de nível de ensino (%)"] = pd.to_numeric(
            df["Taxas de conclusão de nível de ensino (%)"], errors="coerce"
        )

        # ==========================================
        # 6. ORDENAÇÃO
        # ==========================================
        df = df.sort_values(by=["Estado", "Cor/raça"]).reset_index(drop=True)

        # ==========================================
        # 7. ADICIONANDO REGIÃO
        # ==========================================
        df["Região"] = df["Estado"].map(regioes)

        df = df[
            [
                "Região",
                "Estado",
                "Cor/raça",
                "Grupo de idade",
                "Taxas de conclusão de nível de ensino (%)",
            ]
        ]
        salvar_cache(df, "conclusao_cor.csv", agregado)
        msg = "API do IBGE (ao vivo)"
    return df, msg
