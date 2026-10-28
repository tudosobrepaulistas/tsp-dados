#!/usr/bin/env python3
"""Notícia por áudio do TSP: lê a fila do site e grava as matérias que o robô escreveu.

  python3 ferramentas/audio.py fila
      Mostra os envios da redação que ainda não têm matéria em api/audio.json
      (quem fala, clube, link, observação e o texto do áudio transcrito no aparelho do jornalista).
  python3 ferramentas/audio.py adicionar ARQUIVO.json
      ARQUIVO = lista de itens (formato abaixo). Valida e junta em api/audio.json (guarda os 200 mais novos).
      O site confere a cada 15 minutos, monta a matéria e publica sozinho.

Item pronto: {"id": 123, "titulo": "até 100 caracteres", "subtitulo": "até 200",
  "corpo": [{"p": "parágrafo"}, {"h2": "Intertítulo em forma de pergunta?"}, {"citacao": "fala literal"}, ...],
  "resumo": ["3 a 5 tópicos"], "faq": [["pergunta?", "resposta"], ...], "meta_title": "até 60",
  "meta_desc": "até 155", "foco": "palavra-chave", "tags": ["3 a 6"]}
Item recusado: {"id": 123, "erro": "motivo curto, em português, para a redação"}
"""
import datetime
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ARQ = RAIZ / "api" / "audio.json"
FILA = "https://tudosobrepaulista.com.br/wp-json/tsp/v1/fila-audio"


def ler():
    try:
        return json.loads(ARQ.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {"itens": []}


def fila(_a):
    req = urllib.request.Request(FILA, headers={"User-Agent": "TSP-Audio/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            itens = json.loads(r.read().decode("utf-8")).get("itens", [])
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print("Fila vazia (o plugin TSP Notícia por Áudio ainda não está ativo no site).")
            return
        raise
    feitos = {i["id"] for i in ler()["itens"]}
    novos = [i for i in itens if i["id"] not in feitos]
    if not novos:
        print("Fila vazia.")
        return
    for i in novos:
        print(f"=== ID {i['id']} | enviado {i['enviado']} | clubes: {', '.join(i['clubes'])}")
        print(f"Quem fala/ocasião: {i['contexto']}")
        if i.get("link"):
            print(f"Link: {i['link']}")
        if i.get("obs"):
            print(f"Observação da redação: {i['obs']}")
        print(f"Texto do áudio ({len(i['transcricao'])} caracteres):\n{i['transcricao']}\n")


def adicionar(a):
    novos = json.loads(Path(a[0]).read_text(encoding="utf-8"))
    if isinstance(novos, dict):
        novos = [novos]
    erros = []
    for it in novos:
        n = f"id {it.get('id')}"
        if not isinstance(it.get("id"), int):
            erros.append(f"{n}: id precisa ser número")
        if "erro" in it:
            continue
        if not it.get("titulo") or len(it["titulo"]) > 100:
            erros.append(f"{n}: título vazio ou com mais de 100 caracteres")
        if len(it.get("subtitulo", "")) > 200:
            erros.append(f"{n}: subtítulo passa de 200 caracteres")
        corpo = it.get("corpo", [])
        if sum(1 for b in corpo if b.get("p")) < 4:
            erros.append(f"{n}: corpo precisa de pelo menos 4 parágrafos")
        for b in corpo:
            if not (isinstance(b, dict) and len(b) == 1 and list(b)[0] in ("p", "h2", "citacao")):
                erros.append(f"{n}: bloco mal formado {b!r}")
        if len(it.get("meta_desc", "")) > 160 or len(it.get("meta_title", "")) > 65:
            erros.append(f"{n}: meta_title (65) ou meta_desc (160) longos demais")
        if not (3 <= len(it.get("faq", [])) <= 6):
            erros.append(f"{n}: faq precisa de 3 a 6 perguntas")
        for f in it.get("faq", []):
            if not (isinstance(f, list) and len(f) == 2 and f[0].strip().endswith("?")):
                erros.append(f"{n}: pergunta mal formada {f!r}")
        if not (3 <= len(it.get("tags", [])) <= 6):
            erros.append(f"{n}: tags precisam ser de 3 a 6")
        if re.search(r"\b(bets?|odds?|casas? de apostas?|bet365|betano)\b", json.dumps(it, ensure_ascii=False), re.I):
            erros.append(f"{n}: conteúdo de aposta não pode")
    if erros:
        raise SystemExit("ERRO:\n" + "\n".join(erros))
    d = ler()
    ids = {i["id"] for i in novos}
    d["itens"] = ([i for i in d["itens"] if i["id"] not in ids] + novos)[-200:]
    d["gerado"] = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3))).strftime("%Y-%m-%dT%H:%M:00-03:00")
    ARQ.parent.mkdir(exist_ok=True)
    ARQ.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"OK: {len(novos)} item(ns) gravados; total {len(d['itens'])}")


if __name__ == "__main__":
    c = sys.argv[1] if len(sys.argv) > 1 else ""
    {"fila": fila, "adicionar": adicionar}.get(c, lambda a: print(__doc__))(sys.argv[2:])
