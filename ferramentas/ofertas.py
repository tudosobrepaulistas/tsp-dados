#!/usr/bin/env python3
"""Ofertas do Mercado Livre por clube (listas de afiliado do TSP) → api/ofertas.json, que o site lê.

  python3 ferramentas/ofertas.py atualizar
      lê cada lista de dados/ofertas/listas.json (links meli.la do afiliado) e grava nome, preço, preço antigo e foto.
      O clique no site leva para a lista de afiliado (comissão garantida). Lista que falhar mantém as ofertas anteriores.
"""
import datetime
import html
import json
import re
import sys
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36"


def baixar(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "pt-BR,pt;q=0.9"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.geturl(), r.read().decode("utf-8", "replace")


def valor(m):
    return f"{m.group(1)},{(m.group(2) or '0').zfill(2)}" if m else ""


def ler_lista(link):
    final, t = baixar(link)
    if "account-verification" in final or "poly-card" not in t:
        raise RuntimeError("o Mercado Livre não mostrou a lista (verificação ou página diferente)")
    produtos = []
    for c in re.split(r'<div class="andes-card lists-card poly-card', t)[1:]:
        a = re.search(r'<a href="([^"]+)"[^>]*class="poly-component__title"[^>]*>(.*?)</a>', c, re.S)
        if not a:
            continue
        item = re.search(r"wid=(MLB\d+)|item_id%3A(MLB\d+)|/(MLB-?\d+)", a.group(1))
        img = re.search(r'<img[^>]+class="poly-component__picture"[^>]*>', c)
        src = re.search(r'(?:data-src|src)="(https://http2\.mlstatic\.com/[^"]+)"', img.group(0)) if img else None
        i = c.find("poly-price__current")
        atual = valor(re.search(r'aria-label="(?:Ahora:\s*)?([\d.]+)\s*reales?(?:\s*con\s*(\d+)\s*centavos?)?"', c[i:])) if i >= 0 else ""
        antes = valor(re.search(r'aria-label="Antes:\s*([\d.]+)\s*reales?(?:\s*con\s*(\d+)\s*centavos?)?"', c))
        produtos.append({"titulo": html.unescape(re.sub(r"<[^>]+>", "", a.group(2))).strip(), "preco": atual, "preco_antigo": antes,
                         "img": src.group(1) if src else "", "item": next((g for g in item.groups() if g), "").replace("-", "") if item else ""})
    return [p for p in produtos if p["titulo"] and p["img"]]


def atualizar():
    listas = json.loads((RAIZ / "dados" / "ofertas" / "listas.json").read_text(encoding="utf-8"))["listas"]
    arq = RAIZ / "api" / "ofertas.json"
    atual = json.loads(arq.read_text(encoding="utf-8")) if arq.exists() else {"clubes": {}}
    hoje = datetime.date.today().isoformat()
    for clube, link in listas.items():
        try:
            prods = ler_lista(link)
            if prods:
                atual["clubes"][clube] = {"lista": link, "lido_em": hoje, "produtos": prods}
            print(f"{clube}: {len(prods)} produtos")
        except Exception as e:  # noqa: BLE001
            print(f"AVISO {clube}: {e} (mantidas as ofertas anteriores)")
    for clube in list(atual["clubes"]):
        if clube not in listas:
            del atual["clubes"][clube]
    atual["gerado"] = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3))).strftime("%Y-%m-%dT%H:%M:00-03:00")
    arq.write_text(json.dumps(atual, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    if sys.argv[1:2] == ["atualizar"]:
        atualizar()
    else:
        print(__doc__)
