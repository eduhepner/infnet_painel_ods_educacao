import altair as alt
import pandas as pd


def alfabetizacao_sexo(df):
    grafico = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("Estado:N", title="Estado"),
            xOffset=alt.XOffset("Sexo:N"),
            y=alt.Y(
                "Taxa de alfabetização 15+ anos (%):Q",
                title="Taxa de alfabetização 15+ anos (%)",
            ),
            color=alt.Color("Sexo:N", title="Sexo"),
        )
    )
    return grafico


def alfabetizacao_cor(df):
    grafico = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("Estado:N", title="Estado"),
            xOffset=alt.XOffset("Cor/raça:N"),
            y=alt.Y(
                "Taxa de alfabetização 15+ anos (%):Q",
                title="Taxa de alfabetização 15+ anos (%)",
            ),
            color=alt.Color("Cor/raça:N", title="Cor/raça"),
        )
    )
    return grafico


def conclusao_sexo(df):
    grafico = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("Estado:N", title="Estado"),
            xOffset=alt.XOffset("Sexo:N"),
            y=alt.Y(
                "Taxas de conclusão de nível de ensino (%):Q",
                title="Taxas de conclusão de nível de ensino (%)",
            ),
            color=alt.Color("Sexo:N", title="Sexo"),
        )
    )
    return grafico


def conclusao_cor(df):
    grafico = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("Estado:N", title="Estado"),
            xOffset=alt.XOffset("Cor/raça:N"),
            y=alt.Y(
                "Taxas de conclusão de nível de ensino (%):Q",
                title="Taxas de conclusão de nível de ensino (%)",
            ),
            color=alt.Color("Cor/raça:N", title="Cor/raça"),
        )
    )
    return grafico


def escolarizacao_sexo(df):
    grafico = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("Estado:N", title="Estado"),
            xOffset=alt.XOffset("Sexo:N"),
            y=alt.Y(
                "Taxa de escolarização (%):Q",
                title="Taxa de escolarização (%)",
            ),
            color=alt.Color("Sexo:N", title="Sexo"),
        )
    )
    return grafico


def escolarizacao_cor(df):
    grafico = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("Estado:N", title="Estado"),
            xOffset=alt.XOffset("Cor/raça:N"),
            y=alt.Y(
                "Taxa de escolarização (%):Q",
                title="Taxa de escolarização (%)",
            ),
            color=alt.Color("Cor/raça:N", title="Cor/raça"),
        )
    )
    return grafico


def frequencia_sexo(df):
    grafico = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("Estado:N", title="Estado"),
            xOffset=alt.XOffset("Sexo:N"),
            y=alt.Y(
                "Taxa ajustada de frequência escolar (%):Q",
                title="Taxa ajustada de frequência escolar (%)",
            ),
            color=alt.Color("Sexo:N", title="Sexo"),
        )
    )
    return grafico


def frequencia_cor(df):
    grafico = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("Estado:N", title="Estado"),
            xOffset=alt.XOffset("Cor/raça:N"),
            y=alt.Y(
                "Taxa ajustada de frequência escolar (%):Q",
                title="Taxa ajustada de frequência escolar (%)",
            ),
            color=alt.Color("Cor/raça:N", title="Cor/raça"),
        )
    )
    return grafico
