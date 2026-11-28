#!/usr/bin/env python3
"""Radar TSP "Paulistas pelo mundo" (28/11/2026): quem saiu de um clube paulista (base ou profissional) e joga fora do Brasil.

O site lê api/pelo_mundo.json e api/jogos_mundo.json (tema TSP Nova Era 1.14) e mostra:
  - /paulistas-pelo-mundo/            o Radar (números, filtros por clube de origem, país, divisão, base/profissional)
  - /paulistas-pelo-mundo/<id>/       a ficha de cada jogador (trajetória, títulos, próximo jogo, notícias)
  - home: faixa "Paulistas pelo mundo" depois da tabela da Série A, com "Jogos de hoje no mundo"
  - /campeonato/futebol-internacional/: jogos de hoje e amanhã nas ligas do mundo + paulistas lá fora
  - matérias: selo "Paulista pelo mundo · ex-<clube>" quando o título cita um jogador do radar

Uso:
  python3 ferramentas/pelo_mundo.py adicionar --json ARQ.json     (um jogador ou uma lista; mesmo id = atualiza)
  python3 ferramentas/pelo_mundo.py remover ID
  python3 ferramentas/pelo_mundo.py voltou ID --obs "Acertou com o Guarani"   (voltou ao Brasil: sai do radar, fica guardado)
  python3 ferramentas/pelo_mundo.py destaque --json ARQ.json      (gol, título, transferência, marco: 2 fontes)
  python3 ferramentas/pelo_mundo.py jogos --data 2026-11-28 --json ARQ.json   (jogos do dia nas ligas do mundo; substitui o dia)
  python3 ferramentas/pelo_mundo.py listar [--clube guarani] [--pais Portugal]
  python3 ferramentas/pelo_mundo.py numeros --json ARQ.json   (números da temporada e carreira do oGol, página por página)
  python3 ferramentas/pelo_mundo.py gerar     (escreve api/pelo_mundo.json e api/jogos_mundo.json)
  python3 ferramentas/pelo_mundo.py validar

Jogador (JSON):
  {"nome": "Fulano", "nome_completo": "", "posicao": "Atacante", "nascimento": "2001-05-03",
   "origem": [{"slug": "guarani", "tipo": "base", "ate": 2021, "obs": "Sub-17 e Sub-20; estreou no profissional em 2020"}],
        (o 1º é o clube que "revelou"; tipo base = saiu da base, profissional = jogou no time principal; slug = /times/<slug>/)
   "atual": {"clube": "Suwon Bluewings", "pais": "Coreia do Sul", "liga": "K League 2", "divisao": 2, "desde": "2025"},
   "trajetoria": [{"ano": "2021", "clube": "Guarani", "pais": "Brasil", "obs": "Série B, 20 jogos", "fonte": "https://..."}],
   "titulos": [{"ano": 2026, "titulo": "Campeão da K League 2", "fonte": "https://..."}],
   "foto": {"url": "https://...", "credito": "Fulano/Clube", "fonte": "https://..."},     (opcional; só foto real com crédito)
   "fontes": ["https://materia-1", "https://materia-2"]}
  Regras: clube atual com 2 fontes aceitas (CLAUDE.md, mais os grandes jornais e sites oficiais do país) ou 1 anúncio
  oficial do clube estrangeiro + 1 matéria. oGol, Transfermarkt e Sofascore: só para descobrir nomes; nunca são fonte
  nem são copiados. Nada inventado: o que faltar fica vazio e o site mostra "Em atualização".

Jogo do dia (JSON, lista): [{"liga": "campeonato-ingles", "hora": "17:00", "casa": "Arsenal", "fora": "Chelsea",
   "tv": "ESPN e Disney+", "fonte": "https://agenda-de-veiculo-aceito"}]
   Horário de Brasília. "paulistas" é preenchido sozinho (jogadores do radar nos dois clubes).
"""
import argparse
import datetime
import json
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tsp  # noqa: E402

DADOS, API = tsp.DADOS, tsp.API
ARQ = DADOS / "pelo_mundo.json"
ARQ_JOGOS = DADOS / "jogos_mundo.json"
PRIORITARIOS = ["guarani", "pontepreta", "xvdepiracicaba", "portuguesa", "bragantino", "novorizontino",
                "mirassol", "botafogosp", "comercial"]
NOMES_EXTRA = {"xvdepiracicaba": "XV de Piracicaba", "comercial": "Comercial", "guarani": "Guarani", "portuguesa": "Portuguesa",
               "novorizontino": "Novorizontino", "mirassol": "Mirassol"}
TIPOS_DESTAQUE = {"titulo": "Título", "gol": "Gol", "transferencia": "Transferência", "marco": "Marco", "selecao": "Seleção"}

# país => (bandeira, continente, slug da liga principal no menu Internacional)
PAISES = {
    "Inglaterra": ("🏴󠁧󠁢󠁥󠁮󠁧󠁿", "europa", "campeonato-ingles"), "Espanha": ("🇪🇸", "europa", "campeonato-espanhol"),
    "Itália": ("🇮🇹", "europa", "campeonato-italiano"), "Alemanha": ("🇩🇪", "europa", "campeonato-alemao"),
    "França": ("🇫🇷", "europa", "campeonato-frances"), "Portugal": ("🇵🇹", "europa", "campeonato-portugues"),
    "Holanda": ("🇳🇱", "europa", "campeonato-holandes"), "Turquia": ("🇹🇷", "europa", "campeonato-turco"),
    "Bélgica": ("🇧🇪", "europa", "campeonato-belga"), "Escócia": ("🏴󠁧󠁢󠁳󠁣󠁴󠁿", "europa", "campeonato-escoces"),
    "Grécia": ("🇬🇷", "europa", "campeonato-grego"), "Rússia": ("🇷🇺", "europa", "campeonato-russo"),
    "Ucrânia": ("🇺🇦", "europa", "campeonato-ucraniano"), "Suíça": ("🇨🇭", "europa", "campeonato-suico"),
    "Áustria": ("🇦🇹", "europa", "campeonato-austriaco"), "Bulgária": ("🇧🇬", "europa", "campeonato-bulgaro"),
    "Romênia": ("🇷🇴", "europa", "campeonato-romeno"), "Polônia": ("🇵🇱", "europa", "campeonato-polones"),
    "Croácia": ("🇭🇷", "europa", "campeonato-croata"), "Sérvia": ("🇷🇸", "europa", "campeonato-servio"),
    "Dinamarca": ("🇩🇰", "europa", "campeonato-dinamarques"), "Suécia": ("🇸🇪", "europa", "campeonato-sueco"),
    "Noruega": ("🇳🇴", "europa", "campeonato-noruegues"), "República Tcheca": ("🇨🇿", "europa", "campeonato-tcheco"),
    "Chipre": ("🇨🇾", "europa", "campeonato-cipriota"),
    "Argentina": ("🇦🇷", "america-do-sul", "campeonato-argentino"), "Uruguai": ("🇺🇾", "america-do-sul", "campeonato-uruguaio"),
    "Chile": ("🇨🇱", "america-do-sul", "campeonato-chileno"), "Colômbia": ("🇨🇴", "america-do-sul", "campeonato-colombiano"),
    "Paraguai": ("🇵🇾", "america-do-sul", "campeonato-paraguaio"), "Equador": ("🇪🇨", "america-do-sul", "campeonato-equatoriano"),
    "Peru": ("🇵🇪", "america-do-sul", "campeonato-peruano"), "Bolívia": ("🇧🇴", "america-do-sul", "campeonato-boliviano"),
    "Venezuela": ("🇻🇪", "america-do-sul", "campeonato-venezuelano"),
    "Estados Unidos": ("🇺🇸", "america-do-norte", "mls"), "México": ("🇲🇽", "america-do-norte", "campeonato-mexicano"),
    "Costa Rica": ("🇨🇷", "america-do-norte", "campeonato-costarriquenho"), "Honduras": ("🇭🇳", "america-do-norte", "campeonato-hondurenho"),
    "Guatemala": ("🇬🇹", "america-do-norte", "campeonato-guatemalteco"), "El Salvador": ("🇸🇻", "america-do-norte", "campeonato-salvadorenho"),
    "Panamá": ("🇵🇦", "america-do-norte", "campeonato-panamenho"), "Canadá": ("🇨🇦", "america-do-norte", "campeonato-canadense"),
    "Arábia Saudita": ("🇸🇦", "asia", "campeonato-saudita"), "Japão": ("🇯🇵", "asia", "campeonato-japones"),
    "Coreia do Sul": ("🇰🇷", "asia", "campeonato-sul-coreano"), "China": ("🇨🇳", "asia", "campeonato-chines"),
    "Catar": ("🇶🇦", "asia", "campeonato-catari"), "Emirados Árabes": ("🇦🇪", "asia", "campeonato-emiradense"),
    "Tailândia": ("🇹🇭", "asia", "campeonato-tailandes"), "Índia": ("🇮🇳", "asia", "campeonato-indiano"),
    "Irã": ("🇮🇷", "asia", "campeonato-iraniano"), "Uzbequistão": ("🇺🇿", "asia", "campeonato-uzbeque"),
    "Vietnã": ("🇻🇳", "asia", "campeonato-vietnamita"), "Indonésia": ("🇮🇩", "asia", "campeonato-indonesio"),
    "Malásia": ("🇲🇾", "asia", "campeonato-malaio"), "Kuwait": ("🇰🇼", "asia", "campeonato-kuwaitiano"),
    "Austrália": ("🇦🇺", "oceania", "campeonato-australiano"), "Nova Zelândia": ("🇳🇿", "oceania", "campeonato-neozelandes"),
    "Egito": ("🇪🇬", "africa", "campeonato-egipcio"), "Marrocos": ("🇲🇦", "africa", "campeonato-marroquino"),
    "África do Sul": ("🇿🇦", "africa", "campeonato-sul-africano"), "Tunísia": ("🇹🇳", "africa", "campeonato-tunisiano"),
    "Argélia": ("🇩🇿", "africa", "campeonato-argelino"), "Nigéria": ("🇳🇬", "africa", "campeonato-nigeriano"),
    "Angola": ("🇦🇴", "africa", "campeonato-angolano"),
}


def slug(t):
    t = unicodedata.normalize("NFKD", str(t)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def hoje():
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3))).date()


def base():
    return tsp.ler(ARQ, {"_leia": "Radar Paulistas pelo mundo. Não edite à mão: use ferramentas/pelo_mundo.py.",
                         "prioritarios": PRIORITARIOS, "jogadores": [], "destaques": []})


def base_jogos():
    return tsp.ler(ARQ_JOGOS, {"_leia": "Jogos do dia nas ligas do mundo (horário de Brasília). Use ferramentas/pelo_mundo.py jogos.", "dias": {}})


def salvar(arq, d):
    arq.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def times_paulistas():
    t = tsp.ler(DADOS / "clubes_paulistas.json", {"clubes": {}})["clubes"]
    nomes = dict(NOMES_EXTRA)
    for x in tsp.ler(DADOS / "times.json", {}).values():
        if isinstance(x, dict) and x.get("slug_tsp"):
            nomes[x["slug_tsp"]] = x.get("nome") or x["slug_tsp"]
    return t, nomes


def nome_clube(s, nomes):
    return nomes.get(s) or s.replace("-", " ").title()


def erros_jogador(j, paulistas):
    e = []
    if not j.get("nome"):
        e.append("sem nome")
    if not j.get("origem"):
        e.append("sem clube paulista de origem")
    for o in j.get("origem", []):
        if o.get("slug") not in paulistas:
            e.append("origem '%s' não é clube paulista do site" % o.get("slug"))
        if o.get("tipo") not in ("base", "profissional"):
            e.append("origem.tipo deve ser base ou profissional")
    a = j.get("atual") or {}
    if j.get("status", "ativo") == "ativo":
        if not a.get("clube") or not a.get("pais"):
            e.append("sem clube/país atual")
        if a.get("pais") == "Brasil":
            e.append("joga no Brasil: use 'voltou'")
        if a.get("pais") and a["pais"] not in PAISES:
            e.append("país '%s' fora da lista PAISES (acrescente na ferramenta)" % a["pais"])
    f = [x for x in j.get("fontes", []) if str(x).startswith("http")]
    if len(set(f)) < 2:
        e.append("precisa de 2 fontes (URLs)")
    for x in f:
        if re.search(r"ogol|transfermarkt|sofascore|flashscore|fotmob|besoccer|zerozero", x):
            e.append("fonte proibida: " + x)
    return e


def cmd_adicionar(a):
    d = base()
    paulistas, _ = times_paulistas()
    novos = json.loads(Path(a.json).read_text(encoding="utf-8"))
    novos = novos if isinstance(novos, list) else [novos]
    for j in novos:
        j["id"] = j.get("id") or slug(j["nome"])
        j.setdefault("status", "ativo")
        e = erros_jogador(j, paulistas)
        if e:
            sys.exit("%s: %s" % (j["nome"], "; ".join(e)))
        j["conferido"] = hoje().isoformat()
        velho = next((x for x in d["jogadores"] if x["id"] == j["id"]), None)
        if velho:
            velho.update(j)
            print("atualizado:", j["id"])
        else:
            j["entrou"] = hoje().isoformat()
            d["jogadores"].append(j)
            print("novo:", j["id"])
    d["jogadores"].sort(key=lambda x: x["id"])
    salvar(ARQ, d)


def cmd_remover(a):
    d = base()
    d["jogadores"] = [x for x in d["jogadores"] if x["id"] != a.id]
    salvar(ARQ, d)


def cmd_voltou(a):
    d = base()
    for x in d["jogadores"]:
        if x["id"] == a.id:
            x["status"] = "voltou"
            x["obs_status"] = a.obs or ""
            x["conferido"] = hoje().isoformat()
    salvar(ARQ, d)


def cmd_destaque(a):
    d = base()
    ids = {x["id"] for x in d["jogadores"]}
    novos = json.loads(Path(a.json).read_text(encoding="utf-8"))
    for x in (novos if isinstance(novos, list) else [novos]):
        if x.get("tipo") not in TIPOS_DESTAQUE or x.get("jogador") not in ids or len(set(x.get("fontes", []))) < 2 or not x.get("texto"):
            sys.exit("destaque inválido (tipo, jogador do radar, texto e 2 fontes): %s" % x)
        x.setdefault("data", hoje().isoformat())
        x["id"] = x.get("id") or "%s-%s-%s" % (x["data"], x["tipo"], x["jogador"])
        d["destaques"] = [y for y in d["destaques"] if y["id"] != x["id"]] + [x]
    d["destaques"].sort(key=lambda y: y["data"], reverse=True)
    salvar(ARQ, d)


def cmd_jogos(a):
    d = base_jogos()
    lista = json.loads(Path(a.json).read_text(encoding="utf-8"))
    for j in lista:
        if not (j.get("liga") and re.match(r"^\d{2}:\d{2}$", j.get("hora", "")) and j.get("casa") and j.get("fora") and str(j.get("fonte", "")).startswith("http")):
            sys.exit("jogo inválido (liga, hora HH:MM, casa, fora, fonte): %s" % j)
    d["dias"][a.data] = sorted(lista, key=lambda j: j["hora"])
    corte = (hoje() - datetime.timedelta(days=2)).isoformat()
    d["dias"] = {k: v for k, v in sorted(d["dias"].items()) if k >= corte}
    salvar(ARQ_JOGOS, d)
    print(a.data, len(lista), "jogos")


def chave_clube(n):
    return re.sub(r"\b(fc|cf|sc|ac|afc|cd|club|clube|de|the)\b", "", slug(n).replace("-", " ")).replace(" ", "")


def cmd_gerar(a=None):
    d = base()
    paulistas, nomes = times_paulistas()
    ativos = [j for j in d["jogadores"] if j.get("status", "ativo") == "ativo"]
    out = []
    for j in ativos:
        x = dict(j)
        p = PAISES.get(j["atual"]["pais"], ("", "", ""))
        x["atual"] = dict(j["atual"], bandeira=p[0], continente=p[1], liga_slug=j["atual"].get("liga_slug") or p[2])
        x["origem"] = [dict(o, clube=o.get("clube") or nome_clube(o["slug"], nomes)) for o in j["origem"]]
        out.append(x)
    out.sort(key=lambda j: (j["atual"]["pais"], j["atual"].get("divisao") or 9, j["nome"]))
    corte = (hoje() - datetime.timedelta(days=21)).isoformat()
    destaques = [x for x in d["destaques"] if x["data"] >= corte][:12]
    ano = str(hoje().year)
    titulos = sum(1 for j in out for t in j.get("titulos", []) if str(t.get("ano")) == ano)
    api = {
        "_leia": "Gerado por ferramentas/pelo_mundo.py. Não edite.",
        "gerado": datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3))).isoformat(timespec="minutes"),
        "numeros": {"jogadores": len(out), "paises": len({j["atual"]["pais"] for j in out}),
                    "clubes_origem": len({o["slug"] for j in out for o in j["origem"]}), "titulos_ano": titulos, "ano": ano},
        "ligas_ativas": sorted({j["atual"]["liga_slug"] for j in out if j["atual"]["liga_slug"]}),
        "tipos_destaque": TIPOS_DESTAQUE,
        "jogadores": out,
        "destaques": destaques,
    }
    salvar(API / "pelo_mundo.json", api)
    # Jogos do mundo: marca os jogos com jogador do radar
    por_clube = {}
    for j in out:
        por_clube.setdefault(chave_clube(j["atual"]["clube"]), []).append(j["id"])
    jg = base_jogos()
    dias = {}
    for dia, lista in jg["dias"].items():
        dias[dia] = []
        for j in lista:
            j = dict(j)
            j["paulistas"] = por_clube.get(chave_clube(j["casa"]), []) + por_clube.get(chave_clube(j["fora"]), [])
            dias[dia].append(j)
    salvar(API / "jogos_mundo.json", {"_leia": "Gerado por ferramentas/pelo_mundo.py. Horário de Brasília.", "gerado": api["gerado"], "dias": dias})
    print("api/pelo_mundo.json:", len(out), "jogadores ·", api["numeros"]["paises"], "países · jogos em", len(dias), "dias")


def cmd_validar(a=None):
    d = base()
    paulistas, _ = times_paulistas()
    ruins = 0
    for j in d["jogadores"]:
        e = erros_jogador(j, paulistas)
        if e:
            ruins += 1
            print("!", j["id"], "; ".join(e))
    ids = [j["id"] for j in d["jogadores"]]
    if len(ids) != len(set(ids)):
        print("! ids repetidos")
        ruins += 1
    print("ok" if not ruins else "%d com problema" % ruins)
    return ruins


def cmd_listar(a):
    for j in base()["jogadores"]:
        if a.clube and not any(o["slug"] == a.clube for o in j["origem"]):
            continue
        if a.pais and j["atual"].get("pais") != a.pais:
            continue
        print("%-28s %-12s ex-%-18s %s · %s (%s) · conferido %s" % (j["id"], j.get("status"), j["origem"][0]["slug"], j["atual"].get("clube"), j["atual"].get("pais"), j["atual"].get("divisao") or "?", j.get("conferido")))


def cmd_numeros(a):
    """Números da temporada e carreira, lidos à mão na página do jogador no oGol (regra de 15/11 e pedido do
    Thiago em 28/11). Só números: clube atual, transferência e títulos continuam exigindo as fontes de sempre."""
    x = json.loads(Path(a.json).read_text(encoding="utf-8"))
    d = base()
    por_id = {j["id"]: j for j in d["jogadores"]}
    for n in (x if isinstance(x, list) else [x]):
        j = por_id.get(n["id"])
        if not j:
            print("! id não encontrado:", n["id"]); continue
        if "ogol.com.br/jogador/" not in n["fonte"]:
            raise SystemExit("fonte dos números = página do jogador no oGol")
        comp = [{"nome": c[0], "jogos": c[1], "minutos": c[2], "gols": c[3], "assistencias": c[4]} for c in n["comp"] if c[0] != "Total"]
        tot = next((c for c in n["comp"] if c[0] == "Total"), None)
        j["numeros"] = {"temporada": n["temporada"], "ate": n["ate"], "fonte": n["fonte"], "competicoes": comp,
                        "total": {"jogos": tot[1], "minutos": tot[2], "gols": tot[3], "assistencias": tot[4]} if tot else None}
        car = []
        for r in n["carreira"]:
            cl = re.sub(r"\s*\(E\)\s*\[[^\]]*\]", "", r[1])
            cl = re.sub(r"\[S(\d+)\]", r"(sub-\1)", cl).strip()
            e = {"temporada": r[0], "clube": cl, "jogos": r[2], "gols": r[3], "assistencias": r[4]}
            if "(E)" in r[1]:
                e["emprestimo"] = True
            car.append(e)
        j["carreira"] = car
        j["carreira_fonte"] = n["fonte"]
        if not j.get("nascimento") and n.get("nascimento"):
            j["nascimento"] = n["nascimento"]
        print("OK:", j["nome"], "·", n["temporada"], tot[1] if tot else 0, "jogos")
    salvar(ARQ, d)


def cmd_figurinha(a):
    """Grava a figurinha (ilustração TSP feita a partir de foto de referência) como foto do card."""
    from PIL import Image
    d = base()
    j = next((x for x in d["jogadores"] if x["id"] == a.id), None)
    if not j:
        raise SystemExit("id não encontrado")
    destino = API / "figurinhas" / ("mundo-%s.webp" % a.id)
    destino.parent.mkdir(parents=True, exist_ok=True)
    im = Image.open(a.img).convert("RGB")
    lado = min(im.size)
    im = im.crop(((im.width - lado) // 2, 0, (im.width + lado) // 2, lado)).resize((400, 400), Image.LANCZOS)
    im.save(destino, "WEBP", quality=86)
    j["foto"] = {"url": "https://raw.githubusercontent.com/tudosobrepaulistas/tsp-dados/main/api/figurinhas/" + destino.name,
                 "credito": "Figurinha TSP (ilustração)", "fonte": a.ref}
    salvar(ARQ, d)
    print("OK: figurinha de %s gravada (%s)" % (j["nome"], destino.name))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    s = p.add_subparsers(dest="cmd", required=True)
    x = s.add_parser("adicionar"); x.add_argument("--json", required=True); x.set_defaults(f=cmd_adicionar)
    x = s.add_parser("remover"); x.add_argument("id"); x.set_defaults(f=cmd_remover)
    x = s.add_parser("voltou"); x.add_argument("id"); x.add_argument("--obs"); x.set_defaults(f=cmd_voltou)
    x = s.add_parser("destaque"); x.add_argument("--json", required=True); x.set_defaults(f=cmd_destaque)
    x = s.add_parser("jogos"); x.add_argument("--data", required=True); x.add_argument("--json", required=True); x.set_defaults(f=cmd_jogos)
    x = s.add_parser("listar"); x.add_argument("--clube"); x.add_argument("--pais"); x.set_defaults(f=cmd_listar)
    x = s.add_parser("numeros"); x.add_argument("--json", required=True); x.set_defaults(f=cmd_numeros)
    x = s.add_parser("figurinha"); x.add_argument("id"); x.add_argument("--img", required=True); x.add_argument("--ref", required=True); x.set_defaults(f=cmd_figurinha)
    s.add_parser("gerar").set_defaults(f=cmd_gerar)
    s.add_parser("validar").set_defaults(f=lambda a: sys.exit(1 if cmd_validar(a) else 0))
    a = p.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
