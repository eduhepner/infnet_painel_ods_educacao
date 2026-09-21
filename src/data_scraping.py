import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit
from urllib.robotparser import RobotFileParser

import pandas as pd
import requests
from bs4 import BeautifulSoup

BASE = Path(__file__).resolve().parent.parent
RAW = BASE / "data" / "raw"

AGENT = "INFNET-TRABALHO-ACADEMICO-CIENCIA DE DADOS"
HEADER = {"User-Agent": AGENT}
DELAY = 10.0
TIME_LIMIT = 30

SITES = [
    "https://g1.globo.com/educacao",
    "https://agenciabrasil.ebc.com.br/educacao",
    # "https://educacao.uol.com.br",
    # 'https://brasilescola.uol.com.br',
    # 'https://vestibular.brasilescola.uol.com.br',
    # 'https://educador.brasilescola.uol.com.br'
]


def permissao(url):
    rp = RobotFileParser()
    robot = requests.get(
        f"{url}/robots.txt",
        headers=HEADER,
        timeout=TIME_LIMIT,
    ).text
    rp.parse(robot.splitlines())
    delay = rp.crawl_delay(AGENT)
    if delay is None:
        delay = DELAY
    return rp, delay


def scraping(url, rp, delay):
    if not rp.can_fetch(AGENT, url):
        raise PermissionError(f"robots.txt não permite: {url}")

    resposta = requests.get(url, headers=HEADER, timeout=TIME_LIMIT)
    resposta.raise_for_status()
    resposta.encoding = "utf-8"

    time.sleep(delay)
    return resposta.text


def noticias(html):
    sopa = BeautifulSoup(html, "html.parser")
    titulo = sopa.title.text

    lista_links = []
    links = sopa.find_all("a", href=True)

    if "Agência Brasil" in titulo:
        host = "Agência Brasil - EBC"
        url_ebc = "https://agenciabrasil.ebc.com.br"
        for link in links:
            endereco = link["href"]
            filtro = "/noticia/" not in endereco
            if filtro:
                continue
            link = f'{url_ebc}{link["href"]}'
            if link not in lista_links:
                lista_links.append(link)

    elif "G1 Educação" in titulo:
        host = "g1 - Portal de notícias da Globo"
        for link in links:
            endereco = link["href"]
            filtro = ("/noticia/" not in endereco) or (
                "g1.globo.com/educacao/" not in endereco
            )
            if filtro:
                continue
            if endereco not in lista_links:
                lista_links.append(endereco)

    # elif 'UOL' in titulo:
    #   host = 'uol'
    #   for link in links:
    #     endereco = link["href"]
    #     filtro = ("/noticias/" not in endereco) or (("brasilescola.uol" not in endereco) and ('educacao.uol' not in endereco))
    #     if filtro:
    #       continue
    #     if endereco not in lista_links:
    #       lista_links.append(endereco)
    #   return lista_links

    else:
        print("Site não identificado")
        return None

    return lista_links, host


def get_materia(link):
    partes = urlsplit(link)
    base = f"{partes.scheme}://{partes.hostname}"
    arquivo = partes.path.split("/")[-1]

    try:
        rp, delay = permissao(base)
        html = scraping(link, rp, delay)

    except PermissionError as erro:
        print(f"ERRO: {link} - {erro}")
        return None

    return html


def gravar(linhas):
    agora = datetime.now(timezone.utc).astimezone()
    data_arquivo = agora.strftime("%d_%m_%Y")

    RAW.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(linhas)
    df.to_csv(RAW / f"noticias_{data_arquivo}.csv", index=False, encoding="utf-8")


def gravar_metadados(linhas):
    agora = datetime.now(timezone.utc).astimezone()
    data_arquivo = agora.strftime("%d_%m_%Y")
    coletado = agora.strftime("%d/%m/%Y %H:%M")
    # Metadados
    metadados = {"coletado_em": coletado, "sites": SITES, "noticias": len(linhas)}

    with open(RAW / f"noticias_{data_arquivo}.json", "w", encoding="utf-8") as arquivo:
        json.dump(metadados, arquivo, ensure_ascii=False, indent=4)


def coletar():
    linhas = []

    for site in SITES:
        rp, delay = permissao(site)
        html = scraping(site, rp, delay)

        lista_links, host = noticias(html)
        if lista_links is None:
            continue

        for link in lista_links:
            html = get_materia(link)

            if html is None:
                continue

            sopa = BeautifulSoup(html, "html.parser")

            if host == "Agência Brasil - EBC":
                titulo = sopa.find("h1")
                if titulo is None:
                    continue
                titulo = titulo.get_text(" ", strip=True)

                data = sopa.find("div", class_="data").text.strip()
                data = re.search(
                    r"(\d{2}/\d{2}/\d{4})\s*-\s*(\d{2}:\d{2})", data
                ).group()

                paragrafos = []
                for i in sopa.find("div", class_="conteudo-noticia").find_all("p"):
                    if len(i.get_text(" ", strip=True)) > 10:
                        paragrafos.append(i.get_text(" ", strip=True))
                texto = "\n".join(paragrafos)
                palavras = len(texto.split())

            if host == "g1 - Portal de notícias da Globo":
                titulo = sopa.find("h1")
                if titulo is None:
                    continue
                titulo = titulo.get_text(" ", strip=True)

                data = sopa.find(
                    "p", class_="content-publication-data__updated"
                ).text.strip()
                data = (
                    re.search(r"(\d{2}/\d{2}/\d{4})\s*(\d{2}h\d{2})", data)
                    .group()
                    .replace("h", ":")
                    .replace(" ", " - ")
                )

                paragrafos = []
                paragrafos.append(
                    sopa.find("h2", class_="content-head__subtitle").text.strip()
                )

                for i in sopa.find_all("p", class_="content-text__container"):
                    if len(i.get_text(" ", strip=True)) > 10:
                        paragrafos.append(i.get_text(" ", strip=True))
                texto = "\n".join(paragrafos)
                palavras = len(texto.split())

            linha = {
                "titulo": titulo,
                "data": data,
                "texto": texto,
                "palavras": palavras,
                "url": link,
                "fonte": host,
            }
            linhas.append(linha)

    gravar(linhas)
    gravar_metadados(linhas)


inicio = time.perf_counter()

coletar()

tempo_coleta = time.perf_counter() - inicio

print(f"Tempo de coleta: {tempo_coleta:.2f} segundos.")
