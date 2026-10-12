import json
from pathlib import Path
from typing import Literal

import pandas as pd
from fastapi import Body, FastAPI, Query

from api.model.model import Noticia
from src.data_access import (
    buscar_taxa_alfabetizacao_cor,
    buscar_taxa_alfabetizacao_sexo,
    buscar_taxa_conclusao_cor,
    buscar_taxa_conclusao_sexo,
    buscar_taxa_escolarizacao_cor,
    buscar_taxa_escolarizacao_sexo,
    buscar_taxa_frequencia_cor,
    buscar_taxa_frequencia_sexo,
)
from src.news_transform import load_news
from src.transform import filtrar

BASE = Path(__file__).resolve().parent.parent
SRC = BASE / "src"
CACHE = BASE / "data" / "cache"
VERSAO = "0.1"

REGIOES = [
    "Norte",
    "Nordeste",
    "Centro-Oeste",
    "Sudeste",
    "Sul",
]

Regiao = Literal[
    "Norte",
    "Nordeste",
    "Centro-Oeste",
    "Sudeste",
    "Sul",
]


app = FastAPI(
    title="API do Painel ODS Brasil",
    version=VERSAO,
    description=(
        "Principais indicadores públicos acerca da educação no Brasil. "
        "Dados de alfabetização, escolarização, conclusão e frequência, "
        "além das notícias recentes ligadas à Educação."
    ),
)


def get_data(file):
    df = pd.read_csv(CACHE / f"{file}.csv")
    metadados = json.loads((CACHE / f"{file}.json").read_text(encoding="utf-8"))
    return df, metadados


def get_noticias():
    df = pd.read_csv(BASE / "data" / "processed" / "noticias.csv")
    metadados = json.loads(
        (BASE / "data" / "processed" / "noticias.json").read_text(encoding="utf-8")
    )
    return df, metadados


@app.get("/", tags=["sobre"])
async def apresentacao():
    return {
        "api": "Painel ODS Educação Brasil",
        "versao": VERSAO,
        "documentacao": "/docs",
        "rotas": [
            "/alfabetizacao",
            "/conclusao",
            "/escolarizacao",
            "/frequencia",
            "/noticias",
            "/noticias/fontes",
        ],
    }


@app.get("/alfabetizacao", tags=["alfabetizacao"])
async def alfabetizacao(
    tipo: Literal["cor", "sexo"] = Query(...),
    regiao: list[Regiao] | None = Query(None),
    minimo: int = Query(0, ge=0),
):
    regioes = regiao if regiao is not None else REGIOES
    arquivo = f"alfabetizacao_{tipo}"

    if tipo == "cor":
        buscar_taxa_alfabetizacao_cor()
    elif tipo == "sexo":
        buscar_taxa_alfabetizacao_sexo()

    df, metadados = get_data(arquivo)

    df_filtrado = filtrar(df, regioes_select=regioes, taxa_minima=minimo)

    return {
        "metadados": metadados,
        "dados": df_filtrado.to_dict(orient="records"),
    }


@app.get("/conclusao", tags=["conclusao"])
async def conclusao(
    tipo: Literal["cor", "sexo"] = Query(...),
    regiao: list[Regiao] | None = Query(None),
    minimo: int = Query(0, ge=0),
):
    regioes = regiao if regiao is not None else REGIOES
    arquivo = f"conclusao_{tipo}"

    if tipo == "cor":
        buscar_taxa_conclusao_cor()
    elif tipo == "sexo":
        buscar_taxa_conclusao_sexo()

    df, metadados = get_data(arquivo)

    df_filtrado = filtrar(df, regioes_select=regioes, taxa_minima=minimo)

    return {
        "metadados": metadados,
        "dados": df_filtrado.to_dict(orient="records"),
    }


@app.get("/escolarizacao", tags=["escolarizacao"])
async def escolarizacao(
    tipo: Literal["cor", "sexo"] = Query(...),
    regiao: list[Regiao] | None = Query(None),
    minimo: int = Query(0, ge=0),
):
    regioes = regiao if regiao is not None else REGIOES
    arquivo = f"escolarizacao_{tipo}"

    if tipo == "cor":
        buscar_taxa_escolarizacao_cor()
    elif tipo == "sexo":
        buscar_taxa_escolarizacao_sexo()

    df, metadados = get_data(arquivo)

    df_filtrado = filtrar(df, regioes_select=regioes, taxa_minima=minimo)

    return {
        "metadados": metadados,
        "dados": df_filtrado.to_dict(orient="records"),
    }


@app.get("/frequencia", tags=["frequencia"])
async def frequencia(
    tipo: Literal["cor", "sexo"] = Query(...),
    regiao: list[Regiao] | None = Query(None),
    minimo: int = Query(0, ge=0),
):
    regioes = regiao if regiao is not None else REGIOES
    arquivo = f"frequencia_{tipo}"

    if tipo == "cor":
        buscar_taxa_frequencia_cor()
    elif tipo == "sexo":
        buscar_taxa_frequencia_sexo()

    df, metadados = get_data(arquivo)

    df_filtrado = filtrar(df, regioes_select=regioes, taxa_minima=minimo)

    return {
        "metadados": metadados,
        "dados": df_filtrado.to_dict(orient="records"),
    }


@app.get("/noticias", tags=["noticias"])
async def noticias(quantidade: int | None = Query(None, gt=0)):
    df, metadados = get_noticias()
    fontes = [fonte for fonte in metadados["sites"][0].values()]
    data = metadados["coletado_em"]
    if quantidade is not None:
        df = df.iloc[:quantidade]
    return {
        "metadados": {
            "fontes": fontes,
            "coletado_em": data,
        },
        "dados": df.to_dict(orient="records"),
    }


@app.get("/noticias/fontes", tags=["noticias"])
async def fontes():
    _, metadados = get_noticias()
    fontes = [fonte for fonte in metadados["sites"][0].values()]

    return {
        "fontes": fontes,
    }


@app.post("/noticias/enviar")
async def enviar_noticias(noticias: list[Noticia] = Body(min_length=1)):
    return {
        "status": "Noticias recebidas.",
        "quantidade": len(noticias),
        "noticias": [noticia.model_dump(mode="json") for noticia in noticias],
    }
