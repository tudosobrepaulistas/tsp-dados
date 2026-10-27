#!/usr/bin/env python3
"""Editor SEO do TSP: lista as matérias novas do site e grava o que o editor-robô preparou para cada uma.

  python3 ferramentas/materias.py pendentes [--horas 6]
      Lê as matérias publicadas nas últimas N horas (API pública do WordPress) e mostra as que ainda não
      estão em api/materias.json, com o texto puro numerado por parágrafo (para indicar onde entram os H2).
  python3 ferramentas/materias.py adicionar ARQUIVO.json
      ARQUIVO = lista de itens no formato abaixo. Valida e junta em api/materias.json (guarda os 400 mais novos).

Item: {"id": 123, "resumo": ["3 a 5 tópicos curtos"], "faq": [["pergunta", "resposta"], ...],
       "meta_title": "até 60 caracteres", "meta_desc": "até 155 caracteres", "foco": "palavra-chave",
       "tags": ["3 a 6"], "intertitulos": [{"p": 4, "h2": "Intertítulo antes do 4º parágrafo"}]}
O site só preenche o que estiver vazio na matéria; nunca reescreve o texto do jornalista.
"""
import datetime
import html
import json
import re
import sys
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ARQ = RAIZ / "api" / "materias.json"
SITE = "https://tudosobrepaulista.com.br/wp-json/wp/v2/"


def ler():
    try:
        return json.loads(ARQ.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {"itens": []}


def baixar(url):
    req = urllib.request.Request(url, headers={"User-Agent": "TSP-EditorSEO/1.0"})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.loads(r.read().decode("utf-8"))


def texto(h):
    h = re.sub(r"<!--.*?-->", "", h, flags=re.S)
    partes = re.split(r"</p>|<br\s*/?>\s*<br\s*/?>|\n\s*\n", h)
    out = []
    for p in partes:
        t = html.unescape(re.sub(r"<[^>]+>", " ", p))
        t = re.sub(r"\s+", " ", t).strip()
        if len(t) > 40:
            out.append(t)
    return out


def pendentes(a):
    horas = int(a[a.index("--horas") + 1]) if "--horas" in a else 6
    desde = (datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3))) - datetime.timedelta(hours=horas)).strftime("%Y-%m-%dT%H:%M:%S")  # horário do site (Brasília)
    feitos = {i["id"] for i in ler()["itens"]}
    lista = []
    for tipo in ("materia", "posts"):
        try:
            lista += baixar(f"{SITE}{tipo}?after={desde}&per_page=30&_fields=id,link,title,content,times,tags")
        except Exception as e:  # noqa: BLE001
            print(f"AVISO: não consegui ler {tipo}: {e}", file=sys.stderr)
    for m in lista:
        if m["id"] in feitos:
            continue
        print(f"=== ID {m['id']} | {html.unescape(m['title']['rendered'])}\n{m['link']}")
        tem_h2 = bool(re.search(r"<h[23][\s>]", m["content"]["rendered"], re.I))
        print(f"(tem intertítulos: {'sim' if tem_h2 else 'não'}; tags: {len(m.get('tags', []))})")
        for i, p in enumerate(texto(m["content"]["rendered"]), 1):
            print(f"[{i}] {p}")
        print()


def adicionar(a):
    novos = json.loads(Path(a[0]).read_text(encoding="utf-8"))
    if isinstance(novos, dict):
        novos = [novos]
    erros = []
    for it in novos:
        n = f"id {it.get('id')}"
        if not isinstance(it.get("id"), int):
            erros.append(f"{n}: id precisa ser número")
        if len(it.get("meta_desc", "")) > 160:
            erros.append(f"{n}: meta_desc passa de 160 caracteres")
        if len(it.get("meta_title", "")) > 65:
            erros.append(f"{n}: meta_title passa de 65 caracteres")
        if not (3 <= len(it.get("faq", [])) <= 6):
            erros.append(f"{n}: faq precisa de 3 a 6 perguntas")
        for f in it.get("faq", []):
            if not (isinstance(f, list) and len(f) == 2 and f[0].strip().endswith("?")):
                erros.append(f"{n}: pergunta mal formada {f!r}")
        for x in it.get("intertitulos", []):
            if not (isinstance(x.get("p"), int) and x["p"] > 1 and x.get("h2")):
                erros.append(f"{n}: intertítulo mal formado {x!r}")
    if erros:
        raise SystemExit("ERRO:\n" + "\n".join(erros))
    d = ler()
    ids = {i["id"] for i in novos}
    d["itens"] = [i for i in d["itens"] if i["id"] not in ids] + novos
    d["itens"] = d["itens"][-400:]
    d["gerado"] = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3))).strftime("%Y-%m-%dT%H:%M:00-03:00")
    ARQ.parent.mkdir(exist_ok=True)
    ARQ.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"OK: {len(novos)} matéria(s) gravadas; total {len(d['itens'])}")


if __name__ == "__main__":
    c = sys.argv[1] if len(sys.argv) > 1 else ""
    {"pendentes": pendentes, "adicionar": lambda a: adicionar(a)}.get(c, lambda a: print(__doc__))(sys.argv[2:])
