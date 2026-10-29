#!/usr/bin/env python3
"""Base de jogos do Tudo Sobre Paulista (TSP). Só biblioteca padrão do Python.

Comandos (rodar na raiz do repositório):
  python3 ferramentas/tsp.py agenda [--horas 24]
      Jogos das próximas N horas agrupados por horário de início, com a hora da conferência
      (início + 2h10), e os jogos "pendentes" (já deveriam ter terminado e estão sem resultado).
  python3 ferramentas/tsp.py jogo-novo --comp serie_a --data "2026-10-28 19:30" --casa "Santos" --fora "Palmeiras"
      [--rodada 33] [--fase "Semifinal - ida"] [--grupo A] [--estadio "Vila Belmiro"] [--cidade "Santos"] [--fonte URL]
  python3 ferramentas/tsp.py remarcar ID --data "2026-10-29 21:30" [--obs "Remarcado pela CBF"] [--fonte URL]
  python3 ferramentas/tsp.py resultado ID --placar 2x1 --fontes URL1 URL2 [--penaltis 4x3]
      [--gols "casa|Fulano|23|normal; fora|Beltrano|45+2|penalti; casa|Ciclano|80|contra"]
      (tipo: normal, penalti ou contra; "contra" = gol contra a favor do lado indicado)
  python3 ferramentas/tsp.py ocorrencia ID --status atrasado|em_andamento|adiado|suspenso|cancelado
      --obs "o que aconteceu" [--parcial 1x0 --minuto 75] [--fontes URL ...]
  python3 ferramentas/tsp.py calcular      → gera api/tsp.json (o que o site lê), classificações e artilharia
  python3 ferramentas/tsp.py validar       → confere a base (placar x gols, times, datas)
Horários sempre de Brasília (UTC-3).
"""
import datetime
import json
import re
import sys
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DADOS = RAIZ / "dados"
API = RAIZ / "api"
BRT = datetime.timezone(datetime.timedelta(hours=-3))
CONFERIR_APOS = datetime.timedelta(hours=2, minutes=10)
FINAIS = {"encerrado"}
ABERTOS = {"agendado", "atrasado", "em_andamento"}
STATUS = {"agendado": "NS", "atrasado": "NS", "em_andamento": "LIVE", "encerrado": "FT", "adiado": "PST",
          "suspenso": "SUSP", "cancelado": "CANC"}


def ler(p, padrao=None):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return padrao


def gravar(p, dados):
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    Path(p).write_text(json.dumps(dados, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def slug(s):
    s = unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def agora():
    return datetime.datetime.now(BRT)


def data(s):
    s = s.strip().replace("T", " ")
    d = datetime.datetime.strptime(s[:16], "%Y-%m-%d %H:%M")
    return d.replace(tzinfo=BRT)


def iso(d):
    return d.astimezone(BRT).strftime("%Y-%m-%dT%H:%M:00-03:00")


def opc(a, nome, padrao=""):
    return a[a.index(nome) + 1] if nome in a and a.index(nome) + 1 < len(a) else padrao


def opc_lista(a, nome):
    if nome not in a:
        return []
    r = []
    for x in a[a.index(nome) + 1:]:
        if x.startswith("--"):
            break
        r.append(x)
    return r


def competicoes():
    return ler(DADOS / "competicoes.json", {"competicoes": []})["competicoes"]


def comp(chave):
    for c in competicoes():
        if c["chave"] == chave:
            return c
    raise SystemExit(f"ERRO: competição '{chave}' não existe em dados/competicoes.json")


def times():
    return ler(DADOS / "times.json", {})


def jogos_de(chave):
    return ler(DADOS / "jogos" / f"{chave}.json", {"jogos": []})


def todos_os_jogos():
    for c in competicoes():
        for j in jogos_de(c["chave"])["jogos"]:
            yield c["chave"], j


def achar(id_):
    id_ = int(id_)
    for c in competicoes():
        d = jogos_de(c["chave"])
        for j in d["jogos"]:
            if j["id"] == id_:
                return c["chave"], d, j
    raise SystemExit(f"ERRO: jogo {id_} não encontrado")


def salvar_comp(chave, d):
    d["jogos"].sort(key=lambda j: (j["data"], j["id"]))
    gravar(DADOS / "jogos" / f"{chave}.json", d)


def time_chave(nome):
    """Acha o time pelo nome (ou cria). Devolve a chave."""
    t = times()
    s = slug(nome)
    if s in t:
        return s
    for k, v in t.items():
        if slug(v["nome"]) == s or s in [slug(x) for x in v.get("apelidos", [])]:
            return k
    novo = max([v["id"] for v in t.values()] or [900000]) + 1
    t[s] = {"id": novo, "nome": nome.strip(), "slug_tsp": ""}
    gravar(DADOS / "times.json", t)
    print(f"AVISO: time novo cadastrado: {nome} (chave {s}). Se for clube paulista, preencha slug_tsp em dados/times.json.")
    return s


def placar(s):
    m = re.fullmatch(r"\s*(\d+)\s*[xX-]\s*(\d+)\s*", s or "")
    if not m:
        raise SystemExit("ERRO: placar no formato 2x1 (mandante x visitante)")
    return int(m.group(1)), int(m.group(2))


# ---------------- comandos ----------------

def cmd_agenda(a):
    horas = int(opc(a, "--horas", "24"))
    ag = agora()
    fim = ag + datetime.timedelta(hours=horas)
    blocos, pendentes = {}, []
    tm = times()
    for chave, j in todos_os_jogos():
        if j["status"] not in ABERTOS:
            continue
        ini = data(j["data"])
        item = {"id": j["id"], "comp": chave, "jogo": f'{tm[j["casa"]]["nome"]} x {tm[j["fora"]]["nome"]}',
                "inicio": j["data"][:16].replace("T", " "), "status": j["status"]}
        if ini + CONFERIR_APOS <= ag:
            pendentes.append(item)
        elif ag - datetime.timedelta(hours=3) <= ini <= fim:
            conf = (ini + CONFERIR_APOS).strftime("%Y-%m-%d %H:%M")
            blocos.setdefault(conf, []).append(item)
    saida = {"agora": ag.strftime("%Y-%m-%d %H:%M"),
             "conferencias": [{"conferir_em": k, "jogos": v} for k, v in sorted(blocos.items())],
             "pendentes": pendentes}
    print(json.dumps(saida, ensure_ascii=False, indent=1))


def cmd_jogo_novo(a):
    chave = opc(a, "--comp")
    comp(chave)
    d0 = data(opc(a, "--data"))
    casa, fora = time_chave(opc(a, "--casa")), time_chave(opc(a, "--fora"))
    if casa == fora:
        raise SystemExit("ERRO: mandante e visitante iguais")
    d = jogos_de(chave)
    for j in d["jogos"]:
        if j["casa"] == casa and j["fora"] == fora and abs(data(j["data"]) - d0) < datetime.timedelta(days=4):
            print(f"JÁ EXISTE: jogo {j['id']} ({j['data']}). Use remarcar se a data mudou.")
            return
    novo = max([j["id"] for _, j in todos_os_jogos()] or [91000000]) + 1
    j = {"id": novo, "data": iso(d0), "casa": casa, "fora": fora, "status": "agendado",
         "rodada": opc(a, "--rodada"), "fase": opc(a, "--fase"), "grupo": opc(a, "--grupo"),
         "estadio": opc(a, "--estadio"), "cidade": opc(a, "--cidade"),
         "gols_casa": None, "gols_fora": None, "penaltis": "", "minuto": 0, "gols": [], "obs": "",
         "fontes": [x for x in [opc(a, "--fonte")] if x], "atualizado": iso(agora())}
    d["jogos"].append(j)
    salvar_comp(chave, d)
    print(f"OK: jogo {novo} criado ({chave}) {j['data'][:16]} {times()[casa]['nome']} x {times()[fora]['nome']}")


def cmd_remarcar(a):
    chave, d, j = achar(a[0])
    j["data"] = iso(data(opc(a, "--data")))
    if j["status"] == "adiado":
        j["status"] = "agendado"
    obs = opc(a, "--obs")
    if obs:
        j["obs"] = obs
    if opc(a, "--fonte"):
        j["fontes"].append(opc(a, "--fonte"))
    j["atualizado"] = iso(agora())
    salvar_comp(chave, d)
    print(f"OK: jogo {j['id']} remarcado para {j['data'][:16]}")


def cmd_resultado(a):
    chave, d, j = achar(a[0])
    gc, gf = placar(opc(a, "--placar"))
    fontes = opc_lista(a, "--fontes")
    if len(set(fontes)) < 2:
        raise SystemExit("ERRO: resultado só entra com 2 fontes diferentes (--fontes URL1 URL2)")
    gols = []
    for parte in [p for p in opc(a, "--gols").split(";") if p.strip()]:
        x = [s.strip() for s in parte.split("|")]
        if len(x) < 3 or x[0] not in ("casa", "fora"):
            raise SystemExit(f"ERRO: gol mal escrito: '{parte}' (use casa|Jogador|minuto|tipo)")
        gols.append({"lado": x[0], "jogador": x[1], "minuto": x[2], "tipo": (x[3] if len(x) > 3 else "normal") or "normal"})
    if gols:
        n_c = sum(1 for g in gols if g["lado"] == "casa")
        n_f = sum(1 for g in gols if g["lado"] == "fora")
        if (n_c, n_f) != (gc, gf):
            raise SystemExit(f"ERRO: gols listados ({n_c}x{n_f}) não batem com o placar ({gc}x{gf})")
    j.update({"status": "encerrado", "gols_casa": gc, "gols_fora": gf, "gols": gols,
              "penaltis": opc(a, "--penaltis"), "minuto": 90,
              "fontes": list(dict.fromkeys(j.get("fontes", []) + fontes)), "atualizado": iso(agora())})
    if opc(a, "--obs"):
        j["obs"] = opc(a, "--obs")
    salvar_comp(chave, d)
    tm = times()
    print(f"OK: {tm[j['casa']]['nome']} {gc} x {gf} {tm[j['fora']]['nome']} registrado")


def cmd_ocorrencia(a):
    chave, d, j = achar(a[0])
    st = opc(a, "--status")
    if st not in ("atrasado", "em_andamento", "adiado", "suspenso", "cancelado"):
        raise SystemExit("ERRO: --status deve ser atrasado, em_andamento, adiado, suspenso ou cancelado")
    obs = opc(a, "--obs")
    if st in ("adiado", "suspenso", "cancelado") and not obs:
        raise SystemExit("ERRO: diga o que aconteceu em --obs")
    j["status"] = st
    if obs:
        j["obs"] = obs
    if opc(a, "--parcial"):
        j["gols_casa"], j["gols_fora"] = placar(opc(a, "--parcial"))
        j["minuto"] = int(re.sub(r"\D", "", opc(a, "--minuto", "0")) or 0)
    j["fontes"] = list(dict.fromkeys(j.get("fontes", []) + opc_lista(a, "--fontes")))
    j["atualizado"] = iso(agora())
    salvar_comp(chave, d)
    print(f"OK: jogo {j['id']} marcado como {st}")


def classificar(chave, tm):
    base = ler(DADOS / "base" / f"{chave}.json", {"corte": "2000-01-01T00:00:00-03:00", "linhas": []})
    corte = data(base["corte"])
    tab = {}

    def linha(k, g=""):
        if (g, k) not in tab:
            tab[(g, k)] = {"time": k, "grupo": g, "p": 0, "j": 0, "v": 0, "e": 0, "d": 0, "gp": 0, "gc": 0}
        return tab[(g, k)]

    for l in base["linhas"]:
        r = linha(l["time"], l.get("grupo", ""))
        for c in ("p", "j", "v", "e", "d", "gp", "gc"):
            r[c] += int(l.get(c, 0))
    for j in jogos_de(chave)["jogos"]:
        if j["status"] != "encerrado" or data(j["data"]) <= corte or j["gols_casa"] is None:
            continue
        g = j.get("grupo", "")
        c, f = linha(j["casa"], g), linha(j["fora"], g)
        gc, gf = j["gols_casa"], j["gols_fora"]
        for x, pro, contra in ((c, gc, gf), (f, gf, gc)):
            x["j"] += 1
            x["gp"] += pro
            x["gc"] += contra
            if pro > contra:
                x["v"] += 1
                x["p"] += 3
            elif pro == contra:
                x["e"] += 1
                x["p"] += 1
            else:
                x["d"] += 1
    grupos = {}
    for (g, _), r in tab.items():
        grupos.setdefault(g, []).append(r)
    saida = []
    for g in sorted(grupos):
        lst = sorted(grupos[g], key=lambda r: (-r["p"], -r["v"], -(r["gp"] - r["gc"]), -r["gp"], tm.get(r["time"], {}).get("nome", r["time"])))
        saida.append([[i + 1, tm[r["time"]]["id"], tm[r["time"]]["nome"], r["p"], r["j"], r["v"], r["e"], r["d"], r["gp"] - r["gc"], g, r["gp"], r["gc"]] for i, r in enumerate(lst)])
    return saida


def cmd_calcular(a):
    tm = times()
    cps = competicoes()
    fixtures, classif, artilh = [], {}, {}
    for c in cps:
        chave = c["chave"]
        artilh[chave] = {}
        for j in jogos_de(chave)["jogos"]:
            ini = data(j["data"])
            casa, fora = tm[j["casa"]], tm[j["fora"]]
            st = STATUS.get(j["status"], "NS")
            if st == "FT" and j.get("penaltis"):
                st = "PEN"
            eventos = []
            for g in j.get("gols", []):
                autor_lado = g["lado"] if g["tipo"] != "contra" else ("fora" if g["lado"] == "casa" else "casa")
                t = casa if g["lado"] == "casa" else fora
                eventos.append({"time": {"elapsed": int(re.match(r"\d+", g["minuto"]).group()) if re.match(r"\d+", str(g["minuto"])) else 0, "extra": None, "texto": str(g["minuto"])},
                                "team": {"id": t["id"], "name": t["nome"]}, "player": {"name": g["jogador"]},
                                "type": "Goal", "detail": {"normal": "Normal Goal", "penalti": "Penalty", "contra": "Own Goal"}.get(g["tipo"], "Normal Goal")})
                if g["tipo"] != "contra":
                    k = (g["jogador"], j["casa"] if autor_lado == "casa" else j["fora"])
                    artilh[chave][k] = artilh[chave].get(k, 0) + 1
            fixtures.append({
                "liga": chave, "temporada": c["temporada"], "obs": j.get("obs", ""), "fontes": j.get("fontes", []),
                "fixture": {"id": j["id"], "timestamp": int(ini.timestamp()), "status": {"short": st, "elapsed": j.get("minuto") or None},
                            "venue": {"name": j.get("estadio", ""), "city": j.get("cidade", "")}, "referee": ""},
                "league": {"round": " - ".join(x for x in [j.get("fase", ""), (f"Rodada {j['rodada']}" if j.get("rodada") else ""), (f"Grupo {j['grupo']}" if j.get("grupo") else "")] if x)},
                "teams": {"home": {"id": casa["id"], "name": casa["nome"]}, "away": {"id": fora["id"], "name": fora["nome"]}},
                "goals": {"home": j["gols_casa"], "away": j["gols_fora"]}, "penaltis": j.get("penaltis", ""),
                "events": eventos})
        if c["formato"] in ("pontos", "grupos") and ((DADOS / "base" / f"{chave}.json").exists() or jogos_de(chave)["jogos"]):
            g = classificar(chave, tm)
            if g and g[0]:
                classif[chave] = {"grupos": g}
                gravar(API / "classificacao" / f"{chave}.json", classif[chave])
        lista = sorted(({"jogador": k[0], "time": tm[k[1]]["nome"], "time_id": tm[k[1]]["id"], "gols": n} for k, n in artilh[chave].items()), key=lambda x: (-x["gols"], x["jogador"]))
        artilh[chave] = lista
        if lista:
            gravar(API / "artilharia" / f"{chave}.json", lista)
    tsp = {"gerado": iso(agora()), "versao": 1,
           "competicoes": cps,
           "times": {str(v["id"]): {"chave": k, "nome": v["nome"], "slug_tsp": v.get("slug_tsp", ""), "wiki": v.get("wiki", "")} for k, v in tm.items()},
           "jogos": fixtures, "classificacao": classif, "artilharia": {k: v for k, v in artilh.items() if v}}
    gravar(API / "tsp.json", tsp)
    print(f"OK: api/tsp.json com {len(fixtures)} jogos, {len(classif)} classificações")


def cmd_validar(a):
    tm = times()
    erros = 0
    ids = set()
    for chave, j in todos_os_jogos():
        if j["id"] in ids:
            print(f"ERRO: id repetido {j['id']}")
            erros += 1
        ids.add(j["id"])
        for lado in ("casa", "fora"):
            if j[lado] not in tm:
                print(f"ERRO: jogo {j['id']}: time '{j[lado]}' não existe em times.json")
                erros += 1
        if j["status"] == "encerrado" and len(set(j.get("fontes", []))) < 2:
            print(f"ERRO: jogo {j['id']} encerrado com menos de 2 fontes")
            erros += 1
        if j["status"] in ABERTOS and data(j["data"]) + datetime.timedelta(hours=6) < agora():
            print(f"PENDENTE: jogo {j['id']} ({chave}) de {j['data'][:16]} ainda sem resultado")
    print("Base OK" if not erros else f"{erros} erro(s)")
    if erros:
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)
    c, resto = sys.argv[1], sys.argv[2:]
    {"agenda": cmd_agenda, "jogo-novo": cmd_jogo_novo, "remarcar": cmd_remarcar, "resultado": cmd_resultado,
     "ocorrencia": cmd_ocorrencia, "calcular": cmd_calcular, "validar": cmd_validar}.get(c, lambda a: print(__doc__))(resto)
