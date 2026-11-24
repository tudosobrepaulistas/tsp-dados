#!/usr/bin/env python3
"""Ranking das páginas de clube do TSP na busca "notícias do <clube>" (meta do Thiago, 24/11/2026):
top 3 para todo clube do interior e top 5 para os 4 grandes. Guia: diretrizes/ranking-clubes.md.

  python3 ferramentas/ranking.py fila [--n 6]
      Clubes para conferir agora (prioritários a cada 4 dias, 4 grandes a cada 7, A1/A2/A3/Série B a cada 8,
      A4 a cada 10, sem divisão a cada 14), com a busca exata, a meta e a última posição.
  python3 ferramentas/ranking.py pagina SLUG
      Raio-X da página do clube no TSP: endereço, total de matérias, as 3 mais novas (frescor) e o que falta na ficha.
  python3 ferramentas/ranking.py registrar --json ARQUIVO.json
      Lista de conferências: [{"slug": "xvdepiracicaba", "busca": "notícias do XV de Piracicaba",
        "motor": "websearch" | "search_console", "posicao": 4 | null, "url_tsp": "https://...",
        "top": ["gazetaesportiva.com", "band.com.br", ...], "acoes": ["ficha: fundação e estádio"], "obs": ""}]
      posicao null = o TSP não apareceu entre os resultados.
  python3 ferramentas/ranking.py relatorio
      Placar geral (quantos clubes na meta) e a última posição de cada clube, com a variação.
Só biblioteca padrão. Posição do "websearch" é aproximada (outro buscador); a do Search Console é a que vale.
"""
import datetime
import json
import sys
import urllib.request
from pathlib import Path

R = Path(__file__).resolve().parent.parent
ARQ = R / "dados" / "seo" / "ranking_clubes.json"
SITE = "https://tudosobrepaulista.com.br/wp-json/wp/v2/"
BRT = datetime.timezone(datetime.timedelta(hours=-3))
GRANDES = {"corinthians", "palmeiras", "santos", "saopaulo"}
PRIORITARIOS = {"guarani", "pontepreta", "xvdepiracicaba", "portuguesa", "bragantino", "novorizontino", "mirassol",
                "botafogosp", "comercial"}
INTERVALO = {"prioritario": 4, "grande": 7, "redacao": 8, "nacional": 8, "a4": 10, "sem_divisao": 14}
# Busca exata quando o nome sozinho confunde com outro clube ou com outra coisa
BUSCA = {"comercial": "notícias do Comercial de Ribeirão Preto", "botafogosp": "notícias do Botafogo-SP",
         "saobernardo": "notícias do São Bernardo FC", "bragantino": "notícias do Bragantino",
         "nacional": "notícias do Nacional-SP", "portuguesa": "notícias da Portuguesa"}
FEMININOS = ("inter", "portuguesa", "ferroviária", "ferroviaria", "ponte preta", "francana", "matonense", "itapirense",
             "penapolense", "sociedade", "associação", "associacao", "desportiva", "ad ", "aa ")


def ler(p, padrao):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return padrao


def hoje():
    return datetime.datetime.now(BRT)


def clubes():
    out = {}
    for c in ler(R / "maquina" / "clubes.json", {"clubes": []})["clubes"]:
        if c.get("grupo") == "feminino" or c["slug"].endswith("-feminino"):
            continue
        s = c["slug"]
        tipo = "grande" if s in GRANDES else ("prioritario" if s in PRIORITARIOS else c.get("grupo", "sem_divisao"))
        nome = c.get("nome", s)
        de = "da" if nome.lower().startswith(FEMININOS) else "do"
        out[s] = {"nome": nome, "cidade": c.get("cidade", ""), "tipo": tipo, "meta": 5 if s in GRANDES else 3,
                  "busca": BUSCA.get(s, f"notícias {de} {nome}")}
    return out


def base():
    return ler(ARQ, {"_leia": "Conferências da busca 'notícias do <clube>' (ferramentas/ranking.py). posicao null = fora da lista.",
                     "clubes": {}})


def ultima(hist):
    return hist[-1] if hist else None


def cmd_fila(a):
    n = int(a[a.index("--n") + 1]) if "--n" in a else 6
    b = base()["clubes"]
    agora = hoje()
    ordem = ["prioritario", "redacao", "nacional", "a4", "grande", "sem_divisao"]
    fila = []
    for s, c in clubes().items():
        u = ultima(b.get(s, []))
        dias = (agora - datetime.datetime.fromisoformat(u["data"])).days if u else 999
        if dias < INTERVALO.get(c["tipo"], 10):
            continue
        fora_da_meta = not u or u.get("posicao") is None or u["posicao"] > c["meta"]
        fila.append((0 if not u else 1, ordem.index(c["tipo"]) if c["tipo"] in ordem else 9, 0 if fora_da_meta else 1, -dias, s, c, u))
    fila.sort(key=lambda x: x[:4])
    if not fila:
        print("em dia: nenhum clube para conferir agora")
        return
    for _, _, _, _, s, c, u in fila[:n]:
        ult = "nunca conferido" if not u else f"última {u['data'][:10]}: {'posição ' + str(u['posicao']) if u.get('posicao') else 'fora'} ({u.get('motor')})"
        print(f"- {s} | busca: \"{c['busca']}\" | meta: top {c['meta']} | {c['tipo']} | {c['cidade']} | {ult}")
    print(f"({len(fila)} clube(s) na fila; mostrando {min(n, len(fila))})")


def baixar(url):
    req = urllib.request.Request(url, headers={"User-Agent": "TSP-Ranking/1.0"})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.loads(r.read().decode("utf-8"))


def cmd_pagina(a):
    s = a[0]
    c = clubes().get(s, {})
    t = baixar(SITE + f"times?slug={s}&_fields=id,name,count,link")
    if not t:
        raise SystemExit(f"ERRO: clube '{s}' não existe no site")
    t = t[0]
    print(f"{t['name']} | {t['link']} | {t['count']} matérias | busca alvo: \"{c.get('busca', '')}\" (meta top {c.get('meta', 3)})")
    try:
        ms = baixar(SITE + f"materia?times={t['id']}&per_page=3&_fields=date,link,title")
    except Exception:
        ms = []
    for m in ms:
        print(f"  {m['date'][:16]} {m['title']['rendered'][:90]}")
    if ms:
        horas = (hoje().replace(tzinfo=None) - datetime.datetime.fromisoformat(ms[0]["date"])).total_seconds() / 3600
        print(f"  frescor: última matéria há {horas:.0f}h" + ("  ← SEM MATÉRIA NAS ÚLTIMAS 24H" if horas > 24 else ""))
    g = ler(R / "dados" / "guia_clubes.json", {"clubes": {}})["clubes"].get(s, {})
    campos = ["cidade", "estadio", "capacidade", "fundacao", "apelidos", "cores", "rival", "titulos", "campeonatos_2027",
              "site", "instagram", "presidente"]
    falta = [k for k in campos if not g.get(k)]
    print("  ficha: completa" if not falta else f"  ficha: falta {', '.join(falta)}")


def cmd_registrar(a):
    itens = ler(a[a.index("--json") + 1], None)
    if not isinstance(itens, list):
        raise SystemExit("ERRO: o arquivo precisa ser uma lista")
    cl = clubes()
    d = base()
    erros = []
    for i, x in enumerate(itens, 1):
        if x.get("slug") not in cl:
            erros.append(f"item {i}: slug '{x.get('slug')}' não é clube do TSP (maquina/clubes.json)")
        if x.get("motor") not in ("websearch", "search_console"):
            erros.append(f"item {i}: motor precisa ser websearch ou search_console")
        if x.get("posicao") is not None and not (isinstance(x["posicao"], int) and 1 <= x["posicao"] <= 100):
            erros.append(f"item {i}: posicao inteira de 1 a 100, ou null")
    if erros:
        raise SystemExit("ERRO: nada gravado.\n- " + "\n- ".join(erros))
    for x in itens:
        reg = {"data": hoje().isoformat(timespec="minutes"), "busca": x.get("busca") or cl[x["slug"]]["busca"],
               "motor": x["motor"], "posicao": x.get("posicao"), "url_tsp": x.get("url_tsp", ""),
               "top": [str(u) for u in x.get("top", [])][:10], "acoes": [str(u) for u in x.get("acoes", [])][:10],
               "obs": str(x.get("obs", ""))[:300]}
        h = d["clubes"].setdefault(x["slug"], [])
        h.append(reg)
        d["clubes"][x["slug"]] = h[-30:]
    ARQ.parent.mkdir(parents=True, exist_ok=True)
    ARQ.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"OK: {len(itens)} conferência(s) gravada(s)")


def cmd_relatorio(a):
    cl = clubes()
    b = base()["clubes"]
    na_meta = fora = sem = 0
    linhas = []
    for s, c in sorted(cl.items(), key=lambda x: (x[1]["tipo"] != "prioritario", x[1]["tipo"], x[1]["nome"])):
        h = b.get(s, [])
        u = ultima(h)
        if not u:
            sem += 1
            continue
        p = u.get("posicao")
        ant = h[-2].get("posicao") if len(h) > 1 else None
        var = "" if ant is None or p is None else (f" (↑{ant - p})" if p < ant else (f" (↓{p - ant})" if p > ant else " (=)"))
        ok = p is not None and p <= c["meta"]
        na_meta += ok
        fora += not ok
        linhas.append(f"{'✅' if ok else '⬜'} {c['nome']}: {('posição ' + str(p)) if p else 'fora'}{var} | meta top {c['meta']} | {u['data'][:10]} ({u['motor']})")
    print(f"Na meta: {na_meta} | fora da meta: {fora} | ainda não conferidos: {sem} (de {len(cl)} clubes)")
    print("\n".join(linhas))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    {"fila": cmd_fila, "pagina": cmd_pagina, "registrar": cmd_registrar, "relatorio": cmd_relatorio}.get(
        cmd, lambda a: print(__doc__))(sys.argv[2:])
