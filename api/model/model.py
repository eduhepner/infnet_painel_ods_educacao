from datetime import date, datetime

from pydantic import BaseModel, Field, HttpUrl


class Noticia(BaseModel):
    fonte: str
    manchete: str
    data: date | datetime | None = None
    palavras: int | None = Field(default=None, ge=50)
    url: HttpUrl
