#!/usr/bin/env python3
"""Sugestões de pauta do TSP para os times que cada redator cobre.

  python3 ferramentas/pautas.py clubes
      Lista os clubes cobertos pela redação (lidos do site) e as pautas já sugeridas nas últimas 24h para cada um.
  python3 ferramentas/pautas.py adicionar ARQUIVO.json
      ARQUIVO = lista de pautas. Valida e junta em api/pautas.json (guarda só as das últimas 48 horas).

Pauta: {"clube": "palmeiras", "titulo": "sugestão de pauta (não é título de matéria pronto)",
        "resumo": "1 a 3 frases: o que aconteceu e por que vale matéria", "angulo": "ideia de abordagem (opcional)",
        "fontes": [{"nome": "ge", "url": "https://..."}, ...]}
"""
import datetime
import hashlib
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ARQ = RAIZ / "api" / "pautas.json"
SITE = "https://tudosobrepaulista.com.br/wp-json/tsp/v1/cobertura"
BR = datetime.timezone(datetime.timedelta(hours=-3))
PROIBIDO = re.compile(r"sofascore|flashscore|ogol\.|transfermarkt|fotmob|\bbets?\b|bet365|betano|casas? de apostas?|\bodds?\b|palpites?", re.I)


def agora():
    return datetime.datetime.now(BR)


def ler():
    try:
        return json.loads(ARQ.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {"itens": []}


def clubes(_a):
    req = urllib.request.Request(SITE, headers={"User-Agent": "TSP-Pautas/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            c = json.loads(r.read().decode("utf-8")).get("clubes", {})
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print("Nenhum clube (o plugin do Relatório 1.4 ainda não está no site).")
            return
        raise
    if not c:
        print("Nenhum redator marcou times ainda.")
        return
    limite = (agora() - datetime.timedelta(hours=24)).isoformat()
    ja = {}
    for it in ler()["itens"]:
        if it["gerado"] >= limite:
            ja.setdefault(it["clube"], []).append(it["titulo"])
    for slug, nome in c.items():
        print(f"- {slug} | {nome}")
        for t in ja.get(slug, []):
            print(f"    já sugerida: {t}")


def adicionar(a):
    novos = json.loads(Path(a[0]).read_text(encoding="utf-8"))
    if isinstance(novos, dict):
        novos = [novos]
    erros = []
    for it in novos:
        n = f"{it.get('clube')} | {it.get('titulo', '')[:40]}"
        if not re.fullmatch(r"[a-z0-9-]+", it.get("clube", "")):
            erros.append(f"{n}: clube precisa ser o endereço (slug) da lista")
        if not (15 <= len(it.get("titulo", "")) <= 140):
            erros.append(f"{n}: título entre 15 e 140 caracteres")
        f = it.get("fontes", [])
        if not f or not all(str(x.get("url", "")).startswith("https://") for x in f):
            erros.append(f"{n}: precisa de pelo menos 1 fonte com link https")
        if PROIBIDO.search(json.dumps(it, ensure_ascii=False)):
            erros.append(f"{n}: fonte ou tema proibido (estatística raspada ou aposta)")
    if erros:
        raise SystemExit("ERRO:\n" + "\n".join(erros))
    d = ler()
    t = agora()
    for it in novos:
        it["id"] = "p" + hashlib.md5((it["clube"] + it["titulo"]).encode()).hexdigest()[:10]
        it["gerado"] = t.isoformat(timespec="minutes")
        it["quando"] = t.strftime("%d/%m %Hh")
    ids = {i["id"] for i in novos}
    limite = (t - datetime.timedelta(hours=48)).isoformat()
    d["itens"] = [i for i in d["itens"] if i["id"] not in ids and i["gerado"] >= limite] + novos
    d["gerado"] = t.isoformat(timespec="minutes")
    ARQ.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"OK: {len(novos)} pauta(s); total {len(d['itens'])}")


if __name__ == "__main__":
    c = sys.argv[1] if len(sys.argv) > 1 else ""
    {"clubes": clubes, "adicionar": adicionar}.get(c, lambda a: print(__doc__))(sys.argv[2:])
