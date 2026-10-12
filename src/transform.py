import pandas as pd


def filtrar(
    df,
    regioes_select=None,
    grupo_idade=None,
    faixa_etaria=None,
    taxa_minima=None,
):
    if regioes_select:
        df = df[df["Região"].isin(regioes_select)]
    if grupo_idade is not None:
        if "Grupo de idade" in df.columns:
            df = df.loc[df["Grupo de idade"] == grupo_idade]
    if faixa_etaria is not None:
        if "Faixa etária ideal por curso frequentado" in df.columns:
            df = df.loc[df["Faixa etária ideal por curso frequentado"] == faixa_etaria]
    if taxa_minima is not None:
        coluna = df.columns[-1]

        df = df.loc[df[coluna] >= taxa_minima]

    return df


def ordenar(df, opcao_ordem):
    if opcao_ordem == "Estado (A-Z)":
        df = df.sort_values(by=["Estado", "Região"]).reset_index(drop=True)
    if opcao_ordem == "Região (A-Z)":
        df = df.sort_values(by=["Região", "Estado"]).reset_index(drop=True)

    return df
