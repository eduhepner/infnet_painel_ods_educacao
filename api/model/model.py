from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class Noticia(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fonte: str | None = None
    manchete: str = Field(min_length=1)
    data: date | datetime | None = None
    palavras: int | None = Field(default=None, ge=50)
    url: HttpUrl
    texto: str | None = None


class Resumo(BaseModel):
    manchete: str
    tipo_analise: str = "sumarizacao"
    resumo: str
