#!/usr/bin/env python3
"""Motor de estatísticas do TSP (09/11/2026). Chamado por `tsp.py calcular`; não precisa rodar sozinho.

Gera api/times/<chave>.json para cada time com jogos na temporada:
  - jogos de todas as competições (com placar, fase, estádio, escalação resumida);
  - números por competição, em casa e fora;
  - jogadores que entraram em campo: jogos, titular, entrou, substituído, minutos, gols, pênaltis, cartões,
    vitórias/empates/derrotas e aproveitamento COM o jogador em campo e SEM ele, gols marcados e sofridos
    pelo time com ele em campo (pelos minutos dos gols e das substituições);
  - elenco (site oficial) com foto e dados.
E a previsão estatística dos próximos jogos (modelo de Poisson com ataque/defesa da temporada).
Tudo calculado com a base própria do TSP (resultados em 2 fontes, fichas técnicas de veículos e sites oficiais).
"""
import datetime
import json
import math
import re
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DADOS = RAIZ / "dados"
API = RAIZ / "api"


def slug(s):
    s = unicodedata.normalize("NFD", str(s)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def minuto(m):
    """'45+2' → 45.2 ; '90+5' → 90.5 ; '' → None"""
    m = str(m or "").strip()
    x = re.match(r"(\d+)(?:\+(\d+))?", m)
    if not x:
        return None
    return int(x.group(1)) + (int(x.group(2) or 0) / 10)


def linhas_do_time(txt):
    return [[n.strip() for n in l.split(",") if n.strip()] for l in str(txt or "").split(";") if l.strip()]


def ler(p, padrao=None):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return padrao


def gravar(p, d):
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    Path(p).write_text(json.dumps(d, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")


def participacoes(j, lado):
    """Quem jogou por um lado e de que minuto a que minuto (titular 0→90, substituições pelos minutos da ficha)."""
    esc = (j.get("escalacoes") or {}).get(lado) or {}
    if not esc.get("time"):
        return None
    fim = 120 if j.get("penaltis") or "prorroga" in str(j.get("obs", "")).lower() else 90
    p = {}
    for li, linha in enumerate(linhas_do_time(esc["time"])):
        for n in linha:
            p[slug(n)] = {"nome": n, "ini": 0, "fim": fim, "tit": True, "linha": li, "saiu": False}
    for s in esc.get("entraram", []):
        m = minuto(s.get("minuto"))
        k = slug(s.get("jogador", ""))
        if not k:
            continue
        ini = m if m is not None else fim * 0.75  # sem minuto: estimativa (só para "minutos"; marcada como estimada)
        p[k] = {"nome": s["jogador"], "ini": ini, "fim": fim, "tit": False, "linha": None, "saiu": False, "est": m is None}
        ks = slug(s.get("saiu", ""))
        if ks in p:
            p[ks]["fim"] = ini
            p[ks]["saiu"] = True
    for c in (esc.get("cartoes") or {}).get("vermelhos", []):
        k = slug(c.get("jogador", ""))
        m = minuto(c.get("minuto"))
        if k in p and m is not None:
            p[k]["fim"] = min(p[k]["fim"], m)
    return p


def calcular_times(jogos_por_comp, tm, comps):
    """jogos_por_comp: {chave_comp: [jogos]}; tm: times.json; comps: lista de competições."""
    nome_comp = {c["chave"]: c["nome"] for c in comps}
    zero = lambda: {"j": 0, "v": 0, "e": 0, "d": 0, "gp": 0, "gc": 0}
    T = {}
    for comp, jogos in jogos_por_comp.items():
        if comp.startswith("fem_"):
            continue  # o feminino usa os mesmos times na base: páginas de time são do masculino
        for j in jogos:
            for lado, outro in (("casa", "fora"), ("fora", "casa")):
                k = j[lado]
                t = T.setdefault(k, {"jogos": [], "comp": {}, "casa": zero(), "fora": zero(), "geral": zero(), "jog": {}, "com_esc": 0})
                enc = j.get("status") == "encerrado" and j.get("gols_casa") is not None
                item = {"id": j["id"], "comp": comp, "nome_comp": nome_comp.get(comp, comp), "data": j["data"], "fase": j.get("fase", ""),
                        "rodada": j.get("rodada", ""), "mando": lado, "adv": j[outro], "adv_nome": tm.get(j[outro], {}).get("nome", j[outro]),
                        "estadio": j.get("estadio", ""), "status": j.get("status"), "gp": None, "gc": None, "pen": j.get("penaltis", "")}
                if not enc:
                    t["jogos"].append(item)
                    continue
                gp = j["gols_casa"] if lado == "casa" else j["gols_fora"]
                gc = j["gols_fora"] if lado == "casa" else j["gols_casa"]
                res = "v" if gp > gc else ("d" if gp < gc else "e")
                item.update({"gp": gp, "gc": gc, "res": res})
                for x in (t["comp"].setdefault(comp, zero()), t["geral"], t[lado]):
                    x["j"] += 1
                    x[res] += 1
                    x["gp"] += gp
                    x["gc"] += gc
                part = participacoes(j, lado)
                # gols do jogo com minuto, do ponto de vista deste time
                gols_min = []
                for g in j.get("gols", []):
                    do_time = (g["lado"] == lado)  # "lado" já é o lado que marcou (gol contra vem com o lado beneficiado)
                    gols_min.append((minuto(g.get("minuto")), do_time, g))
                if part:
                    t["com_esc"] += 1
                    item["escalacao"] = [[n for n in l] for l in linhas_do_time(j["escalacoes"][lado]["time"])]
                    esc = j["escalacoes"][lado]
                    am = {slug(c.get("jogador", "")) for c in (esc.get("cartoes") or {}).get("amarelos", [])}
                    vm = {slug(c.get("jogador", "")) for c in (esc.get("cartoes") or {}).get("vermelhos", [])}
                    for k2, p in part.items():
                        s = t["jog"].setdefault(k2, {"nome": p["nome"], "jogos": 0, "tit": 0, "ent": 0, "subst": 0, "min": 0, "min_est": False,
                                                       "gols": 0, "pen": 0, "am": 0, "vm": 0, "v": 0, "e": 0, "d": 0, "gp_campo": 0, "gc_campo": 0,
                                                       "linhas": {}, "ultimo": "", "jogos_ids": []})
                        s["jogos"] += 1
                        s["tit" if p["tit"] else "ent"] += 1
                        s["subst"] += 1 if p["saiu"] else 0
                        s["min"] += max(0, round(p["fim"] - p["ini"]))
                        s["min_est"] = s["min_est"] or bool(p.get("est"))
                        s[res] += 1
                        s["am"] += 1 if k2 in am else 0
                        s["vm"] += 1 if k2 in vm else 0
                        if p["linha"] is not None:
                            s["linhas"][str(p["linha"])] = s["linhas"].get(str(p["linha"]), 0) + 1
                        s["ultimo"] = max(s["ultimo"], j["data"])
                        s["jogos_ids"].append(j["id"])
                        for m, do_time, _g in gols_min:
                            if m is None:
                                continue
                            if p["ini"] <= m <= p["fim"]:
                                s["gp_campo" if do_time else "gc_campo"] += 1
                # gols do jogador (mesmo sem escalação)
                for m, do_time, g in gols_min:
                    if do_time and g.get("tipo") != "contra":
                        k2 = slug(g["jogador"])
                        s = t["jog"].setdefault(k2, {"nome": g["jogador"], "jogos": 0, "tit": 0, "ent": 0, "subst": 0, "min": 0, "min_est": False,
                                                       "gols": 0, "pen": 0, "am": 0, "vm": 0, "v": 0, "e": 0, "d": 0, "gp_campo": 0, "gc_campo": 0,
                                                       "linhas": {}, "ultimo": "", "jogos_ids": []})
                        s["gols"] += 1
                        s["pen"] += 1 if g.get("tipo") == "penalti" else 0
                t["jogos"].append(item)
    # aproveitamento sem o jogador (nos jogos com escalação em que ele não entrou)
    saida = {}
    for k, t in T.items():
        esc_jogos = {x["id"]: x for x in t["jogos"] if x.get("escalacao") is not None and x.get("res")}
        for s in t["jog"].values():
            com = set(s["jogos_ids"])
            sem = [x for i, x in esc_jogos.items() if i not in com]
            pts = lambda v, e: v * 3 + e
            s["aprov"] = round(pts(s["v"], s["e"]) / (s["jogos"] * 3) * 100) if s["jogos"] else None
            sv = sum(1 for x in sem if x["res"] == "v")
            se = sum(1 for x in sem if x["res"] == "e")
            s["sem"] = {"j": len(sem), "v": sv, "e": se, "d": len(sem) - sv - se, "aprov": round(pts(sv, se) / (len(sem) * 3) * 100) if sem else None}
            s["min_por_gol"] = round(s["min"] / s["gols"]) if s["gols"] and s["min"] else None
            pass  # jogos_ids fica (página do jogador)
        t["jogos"].sort(key=lambda x: x["data"])
        el = ler(DADOS / "elencos" / f"{k}.json")
        jog = sorted(t["jog"].values(), key=lambda s: (-s["jogos"], -s["min"], s["nome"]))
        # junta dados do elenco (posição, número, foto) aos jogadores
        if el:
            idx = {slug(x["nome"]): x for x in el.get("jogadores", [])}
            for x in el.get("jogadores", []):
                for ap in [x.get("nome_completo", "")] + list(x.get("apelidos", [])):
                    if ap:
                        idx.setdefault(slug(ap), x)
            for s in jog:
                e = idx.get(slug(s["nome"]))
                if e:
                    s["posicao"] = e.get("posicao", "")
                    s["numero"] = e.get("numero")
                    s["foto"] = e.get("foto")
                    s["no_elenco"] = True
        saida[k] = {"time": k, "id": tm[k]["id"], "nome": tm[k]["nome"], "slug_tsp": tm[k].get("slug_tsp", ""),
                    "geral": t["geral"], "casa": t["casa"], "fora": t["fora"],
                    "competicoes": [{"chave": c, "nome": nome_comp.get(c, c), **v} for c, v in t["comp"].items()],
                    "jogos_com_escalacao": t["com_esc"], "jogos": t["jogos"], "jogadores": jog, "elenco": el}
    return saida


def previsoes(jogos_por_comp):
    """Modelo de Poisson simples: força de ataque/defesa de cada time na temporada (todas as competições
    masculinas), com fator casa. Só para jogos agendados de times com 6+ jogos encerrados."""
    est = {}
    tot_g = tot_j = 0
    casa_g = fora_g = 0
    for comp, jogos in jogos_por_comp.items():
        if comp.startswith("fem_"):
            continue
        for j in jogos:
            if j.get("status") != "encerrado" or j.get("gols_casa") is None:
                continue
            for lado, gp, gc in (("casa", j["gols_casa"], j["gols_fora"]), ("fora", j["gols_fora"], j["gols_casa"])):
                e = est.setdefault(j[lado], {"j": 0, "gp": 0, "gc": 0})
                e["j"] += 1
                e["gp"] += gp
                e["gc"] += gc
            tot_g += j["gols_casa"] + j["gols_fora"]
            casa_g += j["gols_casa"]
            fora_g += j["gols_fora"]
            tot_j += 1
    if tot_j < 30:
        return {}
    media = tot_g / (2 * tot_j)
    f_casa = (casa_g / tot_j) / media if media else 1
    f_fora = (fora_g / tot_j) / media if media else 1
    pois = lambda l, k: math.exp(-l) * l ** k / math.factorial(k)
    out = {}
    for comp, jogos in jogos_por_comp.items():
        if comp.startswith("fem_"):
            continue
        for j in jogos:
            if j.get("status") not in ("agendado", "atrasado"):
                continue
            a, b = est.get(j["casa"]), est.get(j["fora"])
            if not a or not b or a["j"] < 6 or b["j"] < 6:
                continue
            ata_a, def_a = (a["gp"] / a["j"]) / media, (a["gc"] / a["j"]) / media
            ata_b, def_b = (b["gp"] / b["j"]) / media, (b["gc"] / b["j"]) / media
            la = max(0.15, ata_a * def_b * media * f_casa)
            lb = max(0.15, ata_b * def_a * media * f_fora)
            pc = pe = pf = 0
            melhor = (0, 0, 0)
            for x in range(8):
                for y in range(8):
                    p = pois(la, x) * pois(lb, y)
                    if x > y:
                        pc += p
                    elif x == y:
                        pe += p
                    else:
                        pf += p
                    if p > melhor[0]:
                        melhor = (p, x, y)
            s = pc + pe + pf
            out[j["id"]] = {"casa": round(pc / s * 100), "empate": round(pe / s * 100), "fora": round(pf / s * 100),
                            "placar": f"{melhor[1]}x{melhor[2]}", "gols_esperados": [round(la, 2), round(lb, 2)],
                            "base": [a["j"], b["j"]]}
    return out


def gerar(jogos_por_comp, tm, comps, agora_iso):
    times_ = calcular_times(jogos_por_comp, tm, comps)
    indice = {}
    for k, d in times_.items():
        d["gerado"] = agora_iso
        corpo = json.dumps(d, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        import hashlib
        indice[k] = {"id": d["id"], "nome": d["nome"], "hash": hashlib.md5(corpo.encode()).hexdigest()[:12]}
        gravar(API / "times" / f"{k}.json", d)
    gravar(API / "times" / "indice.json", {"gerado": agora_iso, "times": indice})
    return len(times_)
