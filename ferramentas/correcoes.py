#!/usr/bin/env python3
"""Editor-chefe do TSP: checagem das matérias dos redatores contra outras fontes.

  python3 ferramentas/correcoes.py listar [--horas 14] [--max 25]
      Matérias publicadas nas últimas N horas (id, data, título, link e o texto limpo), para conferir os fatos.
  python3 ferramentas/correcoes.py apontar ID --gravidade grave|media|leve --motivo "o que está errado"
          --sugestao "como corrigir" --fonte "Nome" URL [--fonte "Nome" URL]
      Grava o apontamento em api/correcoes.json. Erro de informação (grave) exige 2 fontes independentes.
      Depois: commit, push e `python3 ferramentas/correcoes.py avisar-site` (o site avisa o redator e o Vinicios na hora).
  python3 ferramentas/correcoes.py avisar-site
"""
import datetime
import hashlib
import html
import json
import re
import sys
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo

RAIZ = Path(__file__).resolve().parent.parent
ARQ = RAIZ / "api" / "correcoes.json"
SITE = "https://tudosobrepaulista.com.br"
UA = {"User-Agent": "TSP-EditorChefe/1.0"}
PROIBIDOS = ("sofascore", "flashscore", "ogol", "transfermarkt", "fotmob", "google.com/search")


def pegar(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def limpo(h):
    h = re.sub(r"<(script|style|figure)[^>]*>.*?</\1>", " ", h or "", flags=re.S | re.I)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", h))).strip()


def listar(args):
    horas = int(args[args.index("--horas") + 1]) if "--horas" in args else 14
    mx = int(args[args.index("--max") + 1]) if "--max" in args else 25
    depois = (datetime.datetime.now(ZoneInfo("America/Sao_Paulo")) - datetime.timedelta(hours=horas)).strftime("%Y-%m-%dT%H:%M:%S")
    itens = pegar(f"{SITE}/wp-json/wp/v2/materia?after={depois}&per_page={min(mx, 100)}&_fields=id,date,title,link,content,author")
    vistos = {x["id"] for x in carregar()["itens"]}
    for m in itens:
        print("=" * 80)
        print(f"ID {m['id']} · autor {m['author']} · {m['date']}" + (" · JÁ APONTADA" if m["id"] in vistos else ""))
        print(html.unescape(m["title"]["rendered"]))
        print(m["link"])
        print(limpo(m["content"]["rendered"])[:3500])
    print(f"\n{len(itens)} matérias.")


def carregar():
    if ARQ.exists():
        return json.loads(ARQ.read_text(encoding="utf-8"))
    return {"_leia": "Erros apontados pelo editor-chefe automático. O site lê de hora em hora, avisa o redator e o editor-chefe.", "itens": []}


def apontar(args):
    pid = int(args[0])
    def opt(n, d=""):
        return args[args.index(n) + 1] if n in args else d
    g = opt("--gravidade", "grave")
    motivo = opt("--motivo").strip()
    sug = opt("--sugestao").strip()
    fontes = []
    for i, a in enumerate(args):
        if a == "--fonte":
            fontes.append({"nome": args[i + 1], "url": args[i + 2]})
    if g not in ("grave", "media", "leve"):
        sys.exit("gravidade: grave, media ou leve")
    if len(motivo) < 10 or len(sug) < 5:
        sys.exit("Escreva o motivo (o que está errado e o certo) e a sugestão de correção.")
    for f in fontes:
        if not f["url"].startswith("https://") or any(p in f["url"] for p in PROIBIDOS) or re.match(r"^https://[^/]+/?$", f["url"]):
            sys.exit(f"Fonte não aceita (precisa ser o link exato de uma matéria/nota): {f['url']}")
    if g == "grave" and len({re.sub(r'^https://(www\.)?', '', f['url']).split('/')[0] for f in fontes}) < 2:
        sys.exit("Erro de informação (grave) exige 2 fontes independentes (sites diferentes).")
    m = pegar(f"{SITE}/wp-json/wp/v2/materia/{pid}?_fields=id,title,link")
    d = carregar()
    chave = f"{pid}-" + hashlib.sha1(motivo.lower().encode()).hexdigest()[:10]
    if any(x["chave"] == chave for x in d["itens"]):
        sys.exit("Esse apontamento já existe.")
    d["itens"].append({"chave": chave, "id": pid, "titulo": html.unescape(m["title"]["rendered"]), "link": m["link"], "gravidade": g,
                       "motivo": motivo, "sugestao": sug, "fontes": fontes, "em": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")})
    d["itens"] = d["itens"][-300:]
    ARQ.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"OK: apontado na matéria {pid} ({g}).")


def avisar():
    try:
        print(pegar(f"{SITE}/wp-json/tsp/v1/correcoes-ler?x={int(datetime.datetime.now().timestamp())}"))
    except Exception as e:  # noqa
        print("Site não respondeu agora; ele lê sozinho de hora em hora.", e)


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help"):
        print(__doc__)
    elif a[0] == "listar":
        listar(a[1:])
    elif a[0] == "apontar":
        apontar(a[1:])
    elif a[0] == "avisar-site":
        avisar()
    else:
        print(__doc__)
