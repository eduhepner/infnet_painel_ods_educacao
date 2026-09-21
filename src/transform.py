import pandas as pd


def filtrar(
    df_sexo,
    df_cor,
    regioes_select=None,
    grupo_idade=None,
    faixa_etaria=None,
    taxa_minima=None,
):
    if regioes_select:
        df_sexo = df_sexo[df_sexo["Região"].isin(regioes_select)]
        df_cor = df_cor[df_cor["Região"].isin(regioes_select)]
    if grupo_idade is not None:
        if "Grupo de idade" in df_sexo.columns:
            df_sexo = df_sexo.loc[df_sexo["Grupo de idade"] == grupo_idade]
        if "Grupo de idade" in df_cor.columns:
            df_cor = df_cor.loc[df_cor["Grupo de idade"] == grupo_idade]
    if faixa_etaria is not None:
        if "Faixa etária ideal por curso frequentado" in df_sexo.columns:
            df_sexo = df_sexo.loc[
                df_sexo["Faixa etária ideal por curso frequentado"] == faixa_etaria
            ]
        if "Faixa etária ideal por curso frequentado" in df_cor.columns:
            df_cor = df_cor.loc[
                df_cor["Faixa etária ideal por curso frequentado"] == faixa_etaria
            ]
    if taxa_minima is not None:
        coluna_sexo = df_sexo.columns[-1]
        coluna_cor = df_cor.columns[-1]

        df_sexo = df_sexo.loc[df_sexo[coluna_sexo] >= taxa_minima]
        df_cor = df_cor.loc[df_cor[coluna_cor] >= taxa_minima]

    return df_sexo, df_cor


def ordenar(df_sexo, df_cor, opcao_ordem):
    if opcao_ordem == "Estado (A-Z)":
        df_sexo = df_sexo.sort_values(by=["Estado", "Região"]).reset_index(drop=True)
        df_cor = df_cor.sort_values(by=["Estado", "Região"]).reset_index(drop=True)
    if opcao_ordem == "Região (A-Z)":
        df_sexo = df_sexo.sort_values(by=["Região", "Estado"]).reset_index(drop=True)
        df_cor = df_cor.sort_values(by=["Região", "Estado"]).reset_index(drop=True)

    return df_sexo, df_cor
