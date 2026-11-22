#!/usr/bin/env python3
"""Números dos técnicos calculados pela base de jogos do TSP (custo zero: só lê dados/jogos/*.json).

  python3 ferramentas/tecnicos.py gerar        → api/tecnicos.json
  python3 ferramentas/tecnicos.py ver "Nome"   → resumo de um técnico

O técnico de cada lado vem da ficha técnica gravada no jogo (campo escalacoes.casa/fora.tecnico, com fonte).
Para cada técnico: jogos, vitórias, empates, derrotas, aproveitamento, gols pró/contra, por clube, por competição,
lista de jogos e confrontos contra outros técnicos (para cruzar técnico x técnico e clube x clube).
Só jogos encerrados com placar entram. Nada é estimado: técnico sem ficha técnica no jogo não ganha aquele jogo.
"""
import datetime
import glob
import json
import sys
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "api" / "tecnicos.json"


def chave(nome):
    s = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode().lower()
    return "-".join(s.replace(".", " ").split())


def comps():
    meta = {}
    try:
        c = json.loads((RAIZ / "dados" / "competicoes.json").read_text())
        for x in (c.get("competicoes") if isinstance(c, dict) else c) or []:
            if isinstance(x, dict) and x.get("chave"):
                meta[x["chave"]] = x.get("nome") or x["chave"]
    except Exception:  # noqa: BLE001
        pass
    return meta


def nomes_times():
    try:
        t = json.loads((RAIZ / "dados" / "times.json").read_text())
        t = t.get("times", t) if isinstance(t, dict) else t
        if isinstance(t, dict):
            return {k: (v.get("nome") if isinstance(v, dict) else str(v)) for k, v in t.items()}
        return {x.get("chave"): x.get("nome") for x in t if isinstance(x, dict)}
    except Exception:  # noqa: BLE001
        return {}


def gerar():
    meta, tn = comps(), nomes_times()
    tec = {}
    for f in sorted(glob.glob(str(RAIZ / "dados" / "jogos" / "*.json"))):
        comp = Path(f).stem
        d = json.loads(Path(f).read_text())
        for j in (d.get("jogos") if isinstance(d, dict) else d) or []:
            e = j.get("escalacoes") or {}
            if j.get("status") != "encerrado" or j.get("gols_casa") is None or not e:
                continue
            tecs = {l: str((e.get(l) or {}).get("tecnico") or "").strip() for l in ("casa", "fora")}
            for lado, outro in (("casa", "fora"), ("fora", "casa")):
                nome = tecs[lado]
                if not nome:
                    continue
                gp, gc = (j["gols_casa"], j["gols_fora"]) if lado == "casa" else (j["gols_fora"], j["gols_casa"])
                res = "V" if gp > gc else ("D" if gp < gc else "E")
                k = chave(nome)
                t = tec.setdefault(k, {"nome": nome, "jogos": 0, "V": 0, "E": 0, "D": 0, "gp": 0, "gc": 0,
                                       "clubes": {}, "competicoes": {}, "contra": {}, "lista": []})
                t["jogos"] += 1
                t[res] += 1
                t["gp"] += gp
                t["gc"] += gc
                clube = j[lado]
                c = t["clubes"].setdefault(clube, {"nome": tn.get(clube) or clube, "jogos": 0, "V": 0, "E": 0, "D": 0})
                c["jogos"] += 1
                c[res] += 1
                cp = t["competicoes"].setdefault(comp, {"nome": meta.get(comp, comp), "jogos": 0, "V": 0, "E": 0, "D": 0})
                cp["jogos"] += 1
                cp[res] += 1
                adv_tec = tecs[outro]
                if adv_tec:
                    h = t["contra"].setdefault(chave(adv_tec), {"nome": adv_tec, "jogos": 0, "V": 0, "E": 0, "D": 0})
                    h["jogos"] += 1
                    h[res] += 1
                t["lista"].append({"id": j["id"], "data": (j.get("data") or "")[:10], "comp": comp, "clube": clube,
                                   "adversario": j[outro], "mando": lado, "placar": f"{gp}x{gc}", "res": res,
                                   "tecnico_adversario": adv_tec})
    for t in tec.values():
        t["aproveitamento"] = round(100 * (3 * t["V"] + t["E"]) / (3 * t["jogos"]), 1) if t["jogos"] else 0
        t["lista"].sort(key=lambda x: x["data"], reverse=True)
    out = {"gerado": datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3))).isoformat(timespec="minutes"),
           "_leia": "Números dos técnicos pela base de jogos do TSP (fichas técnicas com fonte). Parcial: só jogos com ficha técnica registrada.",
           "tecnicos": dict(sorted(tec.items(), key=lambda kv: -kv[1]["jogos"]))}
    SAIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1))
    print(f"api/tecnicos.json: {len(tec)} técnicos, {sum(t['jogos'] for t in tec.values())} jogos-técnico")


def ver(nome):
    d = json.loads(SAIDA.read_text())
    t = d["tecnicos"].get(chave(nome))
    if not t:
        print("não encontrado")
        return
    print(f"{t['nome']}: {t['jogos']} jogos, {t['V']}V {t['E']}E {t['D']}D, aproveitamento {t['aproveitamento']}%")
    for c in t["clubes"].values():
        print(f"  {c['nome']}: {c['jogos']} jogos {c['V']}V {c['E']}E {c['D']}D")


if __name__ == "__main__":
    if sys.argv[1:2] == ["gerar"]:
        gerar()
    elif sys.argv[1:2] == ["ver"] and len(sys.argv) > 2:
        ver(sys.argv[2])
    else:
        print(__doc__)
