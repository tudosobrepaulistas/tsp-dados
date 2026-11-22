#!/usr/bin/env python3
"""Ficha dos clubes (guia da página do clube).
  python3 ferramentas/guia.py juntar rascunhos/guia-loteN.json [...]   (mescla na base sem apagar o que já existe)
  python3 ferramentas/guia.py gerar                                     (escreve api/guia_clubes.json)
Base: dados/guia_clubes.json. Só campos conferidos; '_pendente', 'obs' e afins ficam fora do site."""
import json, sys
from pathlib import Path
R = Path(__file__).resolve().parent.parent
BASE, API = R / "dados/guia_clubes.json", R / "api/guia_clubes.json"
CAMPOS = ["cidade", "estadio", "capacidade", "fundacao", "apelidos", "mascote", "cores", "rival", "classico", "titulos",
          "campeonatos_2027", "site", "instagram", "youtube", "presidente", "fontes"]

def ler():
    return json.loads(BASE.read_text()) if BASE.exists() else {"clubes": {}}

def juntar(arqs):
    d = ler(); n = 0
    for a in arqs:
        lote = json.loads(Path(a).read_text())
        for slug, f in lote.items():
            if not isinstance(f, dict):
                continue
            c = d["clubes"].setdefault(slug, {})
            for k in CAMPOS:
                v = f.get(k)
                if v in (None, "", [], {}):
                    continue
                if k == "fontes":
                    c[k] = sorted(set(c.get(k, []) + [x for x in v if isinstance(x, str)]))
                elif not c.get(k):
                    c[k] = v
            n += 1
    BASE.write_text(json.dumps(d, ensure_ascii=False, indent=1))
    print(f"{n} clubes mesclados")

def gerar():
    d = ler()
    out = {"gerado": __import__("datetime").datetime.now().isoformat(timespec="minutes"), "clubes": {}}
    for s, c in d["clubes"].items():
        x = {k: v for k, v in c.items() if k in CAMPOS and k != "fontes" and v not in ("", [], None)}
        for k in ("apelidos", "cores", "rival", "classico", "presidente", "estadio", "cidade", "mascote", "fundacao"):
            if isinstance(x.get(k), list):
                x[k] = ", ".join(str(i) for i in x[k] if i)
        if isinstance(x.get("titulos"), list):
            import re
            x["titulos"] = [[re.sub(r"\s*\(Segunda Divis[aã]o\)", "", str(t[0])), str(t[1]) if len(t) > 1 else ""] for t in x["titulos"] if isinstance(t, (list, tuple)) and t]
        if isinstance(x.get("capacidade"), (int, float)):
            x["capacidade"] = f"{int(x['capacidade']):,}".replace(",", ".")
        if x:
            out["clubes"][s] = x
    API.write_text(json.dumps(out, ensure_ascii=False, indent=1))
    print(f"api/guia_clubes.json com {len(out['clubes'])} clubes")

if __name__ == "__main__":
    if sys.argv[1:2] == ["juntar"]:
        juntar(sys.argv[2:])
    elif sys.argv[1:2] == ["gerar"]:
        gerar()
    else:
        print(__doc__)
