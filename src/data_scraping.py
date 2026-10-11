import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlsplit
from urllib.robotparser import RobotFileParser

import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE = Path(__file__).resolve().parent.parent
RAW = BASE / "data" / "raw"

AGENT = "INFNET-TRABALHO-ACADEMICO-CIENCIA DE DADOS"
HEADER = {"User-Agent": AGENT}
DELAY = 10.0
TIME_LIMIT = 30

SITES = [
    {
        "dinamico": "https://g1.globo.com/educacao",
        "estatico": "https://agenciabrasil.ebc.com.br/educacao",
        # "https://educacao.uol.com.br",
        # 'https://brasilescola.uol.com.br',
        # 'https://vestibular.brasilescola.uol.com.br',
        # 'https://educador.brasilescola.uol.com.br'
    }
]


def permissao(url):
    partes = urlsplit(url)
    base = f"{partes.scheme}://{partes.netloc}"

    rp = RobotFileParser()
    resposta = requests.get(
        f"{base}/robots.txt",
        headers=HEADER,
        timeout=TIME_LIMIT,
    )
    resposta.raise_for_status()

    rp.parse(resposta.text.splitlines())

    delay = rp.crawl_delay(AGENT)
    if delay is None:
        delay = DELAY

    return rp, delay


def scrape_static(url, rp, delay):
    if not rp.can_fetch(AGENT, url):
        raise PermissionError(f"robots.txt não permite: {url}")

    resposta = requests.get(url, headers=HEADER, timeout=TIME_LIMIT)
    resposta.raise_for_status()
    resposta.encoding = "utf-8"

    time.sleep(delay)

    sopa = BeautifulSoup(resposta.text, "html.parser")
    titulo = sopa.title.get_text(strip=True) if sopa.title else ""

    if "Agência Brasil" in titulo:
        print("EBC")
        host = "Agência Brasil - EBC"
        url_ebc = "https://agenciabrasil.ebc.com.br"
        lista_links = []
        links = sopa.find_all("a", href=True)
        for link in links:
            endereco = urljoin(url_ebc, link["href"])
            if "/noticia/" not in endereco:
                continue

            if endereco not in lista_links:
                lista_links.append(endereco)

    else:
        print("Site não identificado")
        return None

    return lista_links, host


def scrape_dynamic(url, rp, delay):
    if not rp.can_fetch(AGENT, url):
        raise PermissionError(f"robots.txt não permite: {url}")

    driver = criar_driver(url)
    try:
        wait = WebDriverWait(driver, 10)
        titulo = driver.find_element(By.TAG_NAME, "title").get_attribute("textContent")

        if "G1 Educação" in titulo:
            print("globo")
            host = "g1 - Portal de notícias da Globo"
            wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div._evt h2 a[href]"))
            )

            news = driver.find_elements(By.CSS_SELECTOR, "div._evt h2 a[href]")
            total = len(news)
            tries = 0

            while True:
                print("Total: ", total)
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                try:
                    WebDriverWait(driver, 5).until(
                        lambda d: len(
                            d.find_elements(By.CSS_SELECTOR, "div._evt h2 a[href]")
                        )
                        > total
                    )

                except TimeoutException:
                    tries += 1

                    if tries >= 2:
                        break
                    else:
                        continue

                except Exception as e:
                    print("Mensagem de erro:", e)
                    raise

                news = driver.find_elements(By.CSS_SELECTOR, "div._evt h2 a[href]")
                total = len(news)
                tries = 0

            news = driver.find_elements(By.CSS_SELECTOR, "div._evt h2 a[href]")
            lista_links = [elemento.get_attribute("href") for elemento in news]

            return lista_links, host
        print("Site não identificado")
        return None
    finally:
        driver.quit()


def get_materia(link, rp, delay):
    print("materia")
    try:
        if not rp.can_fetch(AGENT, link):
            raise PermissionError(f"robots.txt não permite: {link}")
        resposta = requests.get(link, headers=HEADER, timeout=TIME_LIMIT)
        resposta.raise_for_status()
        resposta.encoding = "utf-8"
        time.sleep(delay)
        return resposta.text

    except (PermissionError, requests.RequestException) as erro:
        print(f"ERRO: {link} - {erro}")
        return None


def criar_driver(site):
    print("driver")
    # opcoes = Options()
    # opcoes.add_argument("--headless=new")  # executar o navegador sem abrir
    # opcoes.add_argument("--no-sandbox")
    # opcoes.add_argument("--disable-dev-shm-usage")
    # opcoes.add_argument("--window-size=1920,1080")

    # driver = webdriver.Chrome(options=opcoes)

    opcoes = Options()
    opcoes.page_load_strategy = "eager"

    opcoes.add_argument("--headless=new")
    opcoes.add_argument("--no-sandbox")
    opcoes.add_argument("--disable-dev-shm-usage")
    opcoes.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=opcoes)
    driver.set_page_load_timeout(30)

    print("Driver criado!", flush=True)

    try:
        print(f"Abrindo site: {site}", flush=True)
        driver.get(site)
        print("Site carregado!", flush=True)
        return driver
    except Exception:
        driver.quit()
        raise


def gravar(linhas):
    # agora = datetime.now(timezone.utc).astimezone()
    # data_arquivo = agora.strftime("%d_%m_%Y")

    RAW.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(linhas)
    df.to_csv(RAW / f"noticias.csv", index=False, encoding="utf-8")


def gravar_metadados(linhas):
    print("metadados")
    agora = datetime.now(timezone.utc).astimezone()
    data_arquivo = agora.strftime("%d_%m_%Y")
    coletado = agora.strftime("%d/%m/%Y %H:%M")
    # Metadados
    metadados = {"coletado_em": coletado, "sites": SITES, "noticias": len(linhas)}

    with open(RAW / f"noticias.json", "w", encoding="utf-8") as arquivo:
        json.dump(metadados, arquivo, ensure_ascii=False, indent=4)


def coletar():
    print("coletar")
    linhas = []

    for tipo, site in SITES[0].items():

        rp, delay = permissao(site)
        if tipo == "estatico":
            resultado = scrape_static(site, rp, delay)
            if resultado is None:
                continue
        elif tipo == "dinamico":
            resultado = scrape_dynamic(site, rp, delay)
            if resultado is None:
                continue
        lista_links, host = resultado

        for link in lista_links:
            html = get_materia(link, rp, delay)

            if html is None:
                continue

            sopa = BeautifulSoup(html, "html.parser")

            if host == "Agência Brasil - EBC":
                titulo = sopa.find("h1")
                if titulo is None:
                    continue
                titulo = titulo.get_text(" ", strip=True)

                elemento_data = sopa.find("div", class_="data")

                if elemento_data is not None:
                    data_texto = elemento_data.text.strip()
                    data = re.search(
                        r"(\d{2}/\d{2}/\d{4})\s*-\s*(\d{2}:\d{2})", data_texto
                    )

                    if data is not None:
                        data = data.group()
                    else:
                        data = None
                else:
                    data = None

                paragrafos = []
                conteudo = sopa.find("div", class_="conteudo-noticia")
                if conteudo is not None:
                    for i in conteudo.find_all("p"):
                        paragrafo = i.get_text(" ", strip=True)

                        if len(paragrafo) > 10:
                            paragrafos.append(paragrafo)
                texto = "\n".join(paragrafos)
                palavras = len(texto.split())

            if host == "g1 - Portal de notícias da Globo":
                titulo = sopa.find("h1")
                if titulo is None:
                    continue
                titulo = titulo.get_text(" ", strip=True)
                elemento_data = sopa.find(
                    "p", class_="content-publication-data__updated"
                )
                if elemento_data is None:
                    continue

                data = elemento_data.get_text(strip=True)

                resultado_data = re.search(r"(\d{2}/\d{2}/\d{4})\s*(\d{2}h\d{2})", data)

                if resultado_data is None:
                    continue

                data = resultado_data.group().replace("h", ":").replace(" ", " - ")

                paragrafos = []
                subtitulo = sopa.find("h2", class_="content-head__subtitle")
                if subtitulo is not None:
                    paragrafos.append(subtitulo.text.strip())

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
