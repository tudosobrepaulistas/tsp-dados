#!/usr/bin/env python3
"""Mercado da bola do TSP (temporada 2027): quem chega, quem sai e quem renova nos clubes paulistas.

O site lê api/mercado.json (tema TSP Nova Era) e mostra:
  - na home, um carrossel por bloco (Série A, Série B, Feminino, Paulistão A1 a A4);
  - a página /mercado-da-bola/ com tudo, filtrável por bloco e por clube;
  - na página de cada clube, "Mercado da bola" (chegadas, saídas e renovações) e o "Elenco 2027".

Uso:
  python3 ferramentas/mercado.py registrar --json ARQUIVO.json   (um movimento ou uma lista)
  python3 ferramentas/mercado.py remover ID
  python3 ferramentas/mercado.py listar [--dias 7] [--clube palmeiras]
  python3 ferramentas/mercado.py gerar      (escreve api/mercado.json)
  python3 ferramentas/mercado.py validar
  python3 ferramentas/mercado.py figurinhas [--clube ituano] [--max 10]   (fila de figurinhas com IA: prompt de cada reforço sem foto)
  python3 ferramentas/mercado.py figurinha ID --img ARQUIVO.png --ref URL_DA_FOTO_DE_REFERENCIA   (grava a figurinha pronta)

Movimento (JSON):
  {"data": "2026-11-13", "jogador": "Fulano", "posicao": "Atacante",
   "de": "Flamengo", "para": "Palmeiras",           (renovação: de = para)
   "de_slug": "", "para_slug": "palmeiras",          (clube paulista: endereço /times/<slug>/; em branco o sistema tenta achar)
   "tipo": "contratacao",                            (contratacao, emprestimo, venda, saida, retorno, renovacao, promovido)
   "situacao": "oficial",                            (oficial = clube anunciou; acertado = 2 veículos dizem que está fechado)
   "feminino": false, "obs": "contrato até dezembro de 2028",
   "foto": {"url": "https://...", "credito": "Fulano/Clube", "fonte": "https://página-da-foto"},   (opcional)
   "fontes": ["https://anuncio-oficial", "https://materia-de-veiculo-aceito"]}
  "de" pode ficar vazio só em contratação quando a fonte não diz de onde o jogador veio.
  Clubes pequenos (Paulistão A2 a A4, sem site): vale 1 matéria de veículo aceito que relata o anúncio oficial do clube,
  marcando "anuncio_do_clube": true (situacao "oficial").

Regras (as mesmas da base): nada inventado, 2 fontes aceitas (CLAUDE.md). oGol e Transfermarkt podem ser consultados
como referência para descobrir e conferir movimentos, mas não valem como fonte e nada é copiado deles.
Boato/sondagem não entra. Sem foto oficial com crédito, o site mostra a inicial do jogador.
"""
import datetime
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tsp  # noqa: E402

DADOS, API = tsp.DADOS, tsp.API
ARQ = DADOS / "mercado.json"
TIPOS = {"contratacao": "Contratação", "emprestimo": "Empréstimo", "venda": "Venda", "saida": "Saída",
         "retorno": "Volta de empréstimo", "renovacao": "Renovação", "promovido": "Subiu da base"}
SITUACOES = {"oficial": "Oficial", "acertado": "Acertado"}
FEM = {"corinthians": "corinthians-feminino", "palmeiras": "palmeiras-feminino", "sao paulo": "sao-paulo-feminino",
       "santos": "santos-feminino", "ferroviaria": "ferroviaria-feminino", "bragantino": "red-bull-bragantino-feminino",
       "red bull bragantino": "red-bull-bragantino-feminino", "mirassol": "mirassol-feminino", "taubate": "taubate-feminino"}


def base():
    return tsp.ler(ARQ, {"_leia": "Movimentos do mercado da bola. Não edite à mão: use ferramentas/mercado.py.", "temporada": 2027, "itens": []})


def paulistas():
    return tsp.ler(DADOS / "clubes_paulistas.json", {"clubes": {}})["clubes"]


def norm(s):
    return tsp.slug(s or "").replace("-", " ")


def resolver(nome, slug_dado, feminino, tm, pl):
    """Devolve (slug_tsp, id_base, chave_base) do clube."""
    chave_b, id_b = "", 0
    for k, v in tm.items():
        if norm(v["nome"]) == norm(nome) or k == tsp.slug(nome):
            chave_b, id_b = k, v["id"]
            if not slug_dado:
                slug_dado = v.get("slug_tsp", "")
            break
    if feminino:
        n = norm(nome).replace(" feminino", "")
        slug_dado = slug_dado if slug_dado.endswith("feminino") else FEM.get(n, "")
        id_b = 0  # escudo do feminino vem do clube no site
    if slug_dado not in pl:
        slug_dado = ""
    return slug_dado, id_b, chave_b


def checar(m, tm, pl):
    e = []
    try:
        datetime.date.fromisoformat(str(m.get("data", "")))
    except ValueError:
        e.append("data = AAAA-MM-DD (dia do anúncio)")
    for c in ("jogador", "para"):
        if not str(m.get(c, "")).strip():
            e.append(f"falta '{c}'")
    if not str(m.get("de", "")).strip() and m.get("tipo") not in ("contratacao", "promovido"):
        e.append("falta 'de' (só pode ficar vazio em contratação/promovido quando a fonte não diz de onde veio)")
    if m.get("posicao") and m["posicao"] not in tsp.POSICOES:
        e.append(f"posicao: {', '.join(tsp.POSICOES)}")
    if m.get("tipo") not in TIPOS:
        e.append(f"tipo: {', '.join(TIPOS)}")
    if m.get("situacao") not in SITUACOES:
        e.append("situacao: oficial ou acertado (boato não entra)")
    f = [str(u) for u in m.get("fontes", [])]
    if m.get("anuncio_do_clube") and m.get("situacao") != "oficial":
        e.append("anuncio_do_clube só vale com situacao oficial")
    minimo = 1 if m.get("anuncio_do_clube") else 2
    if len(set(f)) < minimo or any(not u.startswith("https://") or tsp.FONTE_RUIM.search(u) for u in f):
        e.append("fontes: 2 links https de fontes aceitas (ou 1 matéria de veículo aceito que relata o anúncio oficial do clube, com anuncio_do_clube: true); oGol/Transfermarkt só como referência")
    ft = m.get("foto")
    if ft and (not str(ft.get("url", "")).startswith("https://") or not ft.get("credito") or not ft.get("fonte")):
        e.append("foto precisa de url https, credito e fonte")
    if m.get("nascimento"):
        try:
            datetime.date.fromisoformat(str(m["nascimento"]))
        except ValueError:
            e.append("nascimento = AAAA-MM-DD (só com fonte)")
    nm = m.get("numeros_2026")
    if nm and (not str(nm.get("fonte", "")).startswith("https://") or tsp.FONTE_RUIM.search(str(nm.get("fonte", "")))):
        e.append("numeros_2026 precisa de 'fonte' (matéria aceita; oGol/Transfermarkt não valem)")
    for lado in ("de", "para"):
        s = m.get(f"{lado}_slug", "")
        if s and s not in pl:
            e.append(f"{lado}_slug '{s}' não é clube paulista do site (dados/clubes_paulistas.json)")
    sd = resolver(m.get("de", ""), m.get("de_slug", ""), m.get("feminino"), tm, pl)[0]
    sp = resolver(m.get("para", ""), m.get("para_slug", ""), m.get("feminino"), tm, pl)[0]
    if not sd and not sp:
        e.append("nenhum dos clubes é paulista do site: preencha de_slug ou para_slug")
    return e


def cmd_registrar(a):
    tm, pl = tsp.times(), paulistas()
    x = json.loads(Path(tsp.opc(a, "--json")).read_text(encoding="utf-8"))
    novos = x if isinstance(x, list) else [x]
    b = base()
    ids = {m["id"]: i for i, m in enumerate(b["itens"])}
    erros = 0
    for m in novos:
        m.setdefault("feminino", False)
        e = checar(m, tm, pl)
        if e:
            print(f"ERRO ({m.get('jogador', '?')}):\n  " + "\n  ".join(e))
            erros += 1
            continue
        m["id"] = m.get("id") or tsp.slug(f"{m['data']}-{m['jogador']}-{m['para']}")
        m["atualizado"] = tsp.iso(tsp.agora())
        if m["id"] in ids:
            b["itens"][ids[m["id"]]] = m
            print(f"OK (atualizado): {m['jogador']} · {m['de']} → {m['para']}")
        else:
            b["itens"].append(m)
            ids[m["id"]] = len(b["itens"]) - 1
            print(f"OK: {m['jogador']} · {m['de']} → {m['para']} ({TIPOS[m['tipo']]})")
    b["itens"].sort(key=lambda m: (m["data"], m["id"]), reverse=True)
    tsp.gravar(ARQ, b)
    if erros:
        sys.exit(1)


def cmd_remover(a):
    b = base()
    antes = len(b["itens"])
    b["itens"] = [m for m in b["itens"] if m["id"] != a[0]]
    tsp.gravar(ARQ, b)
    print("removido" if len(b["itens"]) < antes else "id não encontrado")


def cmd_listar(a):
    dias = int(tsp.opc(a, "--dias", "3650"))
    cl = tsp.opc(a, "--clube")
    lim = (datetime.date.today() - datetime.timedelta(days=dias)).isoformat()
    n = 0
    for m in base()["itens"]:
        if m["data"] >= lim and (not cl or cl in (m.get("de_slug"), m.get("para_slug"), tsp.slug(m["de"]), tsp.slug(m["para"]))):
            print(f"{m['data']} | {m['jogador']} | {m['de']} → {m['para']} | {m['tipo']} | {m['situacao']} | {m['id']}")
            n += 1
    print(f"{n} movimento(s)")


def foto_do_elenco(nome, chaves):
    for k in chaves:
        el = tsp.ler(DADOS / "elencos" / f"{k}.json") if k else None
        for j in (el or {}).get("jogadores", []):
            if norm(j.get("nome")) == norm(nome) and j.get("foto", {}).get("url"):
                return j["foto"]
    return None


def numeros_da_base(nome, chaves):
    """Números de 2026 do jogador na base do TSP (jogos com escalação conferida em fonte aceita)."""
    for k in chaves:
        t = tsp.ler(API / "times" / f"{k}.json") if k else None
        for j in (t or {}).get("jogadores", []):
            if norm(j.get("nome")) == norm(nome) and j.get("jogos"):
                return {"jogos": j["jogos"], "gols": j.get("gols", 0), "minutos": j.get("min", 0),
                        "minutos_estimados": bool(j.get("min_est")), "clube": t.get("nome", ""),
                        "fonte": "Base TSP (fichas técnicas conferidas)"}
    return None


def nascimento_do_elenco(nome, chaves):
    for k in chaves:
        el = tsp.ler(DADOS / "elencos" / f"{k}.json") if k else None
        for j in (el or {}).get("jogadores", []):
            if norm(j.get("nome")) == norm(nome) and j.get("nascimento"):
                return j["nascimento"]
    return None


def cmd_gerar(a):
    tm, pl = tsp.times(), paulistas()
    b = base()
    saida = []
    for m in b["itens"]:
        if checar(m, tm, pl):
            continue
        sd, idd, cd = resolver(m["de"], m.get("de_slug", ""), m.get("feminino"), tm, pl)
        sp, idp, cp = resolver(m["para"], m.get("para_slug", ""), m.get("feminino"), tm, pl)
        blocos = sorted(set(pl.get(sd, []) + pl.get(sp, [])))
        foto = m.get("foto") or foto_do_elenco(m["jogador"], [cp, cd])
        numeros = m.get("numeros_2026") or numeros_da_base(m["jogador"], [cd, cp] if m["tipo"] != "renovacao" else [cp])
        nasc = m.get("nascimento") or nascimento_do_elenco(m["jogador"], [cp, cd])
        saida.append({"id": m["id"], "data": m["data"], "jogador": m["jogador"], "posicao": m.get("posicao", ""),
                      "tipo": m["tipo"], "tipo_nome": TIPOS[m["tipo"]], "situacao": m["situacao"],
                      "feminino": bool(m.get("feminino")), "obs": m.get("obs", ""),
                      "de": {"nome": m["de"], "slug": sd, "id": idd},
                      "para": {"nome": m["para"], "slug": sp, "id": idp},
                      "blocos": blocos, "foto": foto or {}, "fontes": m["fontes"][:3],
                      "nascimento": nasc or "", "numeros": numeros or {}})
    tsp.gravar(API / "mercado.json", {"gerado": tsp.iso(tsp.agora()), "temporada": b.get("temporada", 2027),
                                      "tipos": TIPOS, "itens": saida})
    print(f"OK: api/mercado.json com {len(saida)} movimento(s)")
    print(f"OK: api/elencos.json com {gerar_elencos(saida, tm, pl)} elenco(s)")


CHEGA = {"contratacao", "emprestimo", "retorno", "promovido"}
SAI = {"venda", "saida", "emprestimo"}


def gerar_elencos(itens, tm, pl):
    """Elenco 2027 de cada clube paulista do site: elenco do site oficial (dados/elencos) + chegadas oficiais do mercado,
    sem quem saiu oficialmente. Chave = endereço do clube no site."""
    saida = {}
    for f in sorted((DADOS / "elencos").glob("*.json")):
        el = tsp.ler(f)
        s = tm.get(f.stem, {}).get("slug_tsp") or (f.stem if f.stem in pl else "")
        if not s or not el:
            continue
        saida[s] = {"atualizado": el.get("atualizado", ""), "fonte": el.get("fonte", ""),
                    "jogadores": [dict(j) for j in el.get("jogadores", [])], "chegaram": [], "sairam": []}
    for m in sorted(itens, key=lambda m: m["data"]):
        if m["situacao"] != "oficial" or m["tipo"] == "renovacao":
            continue
        d, p = m["de"]["slug"], m["para"]["slug"]
        if d in saida and m["tipo"] in SAI and d != p:
            antes = len(saida[d]["jogadores"])
            saida[d]["jogadores"] = [j for j in saida[d]["jogadores"] if norm(j["nome"]) != norm(m["jogador"])]
            saida[d]["sairam"].append({"nome": m["jogador"], "para": m["para"]["nome"], "tipo": m["tipo_nome"], "data": m["data"],
                                       "estava_no_elenco": len(saida[d]["jogadores"]) < antes})
        if p in saida and m["tipo"] in CHEGA and d != p:
            if not any(norm(j["nome"]) == norm(m["jogador"]) for j in saida[p]["jogadores"]):
                saida[p]["jogadores"].append({"nome": m["jogador"], "posicao": m["posicao"], "foto": m["foto"] or None, "novo": True})
            else:
                for j in saida[p]["jogadores"]:
                    if norm(j["nome"]) == norm(m["jogador"]):
                        j["novo"] = True
            saida[p]["chegaram"].append({"nome": m["jogador"], "de": m["de"]["nome"], "tipo": m["tipo_nome"], "data": m["data"]})
    tsp.gravar(API / "elencos.json", {"gerado": tsp.iso(tsp.agora()), "temporada": 2027, "clubes": saida})
    return len(saida)


PRIORIDADE = ["a", "b", "fem", "d1", "d2", "d3", "d4"]
PROMPT = ("Gere uma imagem: retrato para FIGURINHA DE ÁLBUM DE FUTEBOL, formato quadrado 1:1, estilo foto de estúdio "
          "levemente ilustrada, do jogador da PRIMEIRA imagem anexada, com rosto e cabelo fiéis à referência. Ele veste a camisa do "
          "{clube} nas cores do clube ({cores}). No peito, do lado esquerdo do jogador, o escudo do clube EXATAMENTE como na "
          "SEGUNDA imagem anexada (mesmo desenho, cores e escrita), nítido, como escudo bordado. SEM patrocinadores, SEM número, "
          "SEM nenhum outro texto. Do peito para cima, de frente, fundo liso em degradê das cores do clube, sem moldura. "
          "(Jogadores seguintes do mesmo clube: na MESMA conversa, 'mesmo padrão das anteriores' + nova referência.)")


def cmd_figurinhas(a):
    """Fila de figurinhas: reforços (chegadas) sem foto, por prioridade de bloco."""
    tm, pl = tsp.times(), paulistas()
    cl, mx = tsp.opc(a, "--clube"), int(tsp.opc(a, "--max", "10"))
    cores = tsp.ler(DADOS / "cores_clubes.json", {})
    fila = []
    for m in base()["itens"]:
        if m.get("foto") or m["tipo"] not in CHEGA or m["situacao"] != "oficial":
            continue
        sp = resolver(m["para"], m.get("para_slug", ""), m.get("feminino"), tm, pl)[0]
        if cl and cl != sp:
            continue
        bl = pl.get(sp, ["d4"])
        fila.append((min(PRIORIDADE.index(b) for b in bl), m, sp))
    fila.sort(key=lambda x: (x[0], x[1]["data"]), reverse=False)
    for _, m, sp in fila[:mx]:
        print(f"--- {m['id']}\nPROMPT: " + PROMPT.format(clube=m["para"], cores=cores.get(sp, "cores oficiais"),
              ))
        print("FONTES (procure a foto oficial de anúncio):", " ".join(m["fontes"]))
    print(f"{len(fila)} reforço(s) sem figurinha")
    print("Lembrete: figurinha só com foto oficial de referência do jogador; sem referência, não gere (nada de rosto inventado).")


def cmd_figurinha(a):
    """Grava a figurinha gerada: converte para webp 400x400 em api/figurinhas/ e liga ao movimento."""
    from PIL import Image
    mid, img, ref = a[0], tsp.opc(a, "--img"), tsp.opc(a, "--ref")
    if not ref.startswith("https://"):
        raise SystemExit("ERRO: --ref = link https da foto oficial usada como referência")
    b = base()
    m = next((x for x in b["itens"] if x["id"] == mid), None)
    if not m:
        raise SystemExit("id não encontrado")
    destino = API / "figurinhas" / f"{mid}.webp"
    destino.parent.mkdir(parents=True, exist_ok=True)
    im = Image.open(img).convert("RGBA")
    esc = tsp.opc(a, "--escudo")
    if esc:
        from PIL import ImageFilter
        cx, cy = (float(x) for x in tsp.opc(a, "--pos", "0.645,0.665").split(","))
        e = Image.open(esc).convert("RGBA")
        w = int(im.width * 0.085)
        e = e.resize((w, int(w * e.height / e.width)), Image.LANCZOS)
        sombra = Image.new("RGBA", e.size, (0, 0, 0, 0))
        sombra.putalpha(e.split()[3].point(lambda v: int(v * 0.45)))
        sombra = sombra.filter(ImageFilter.GaussianBlur(3))
        x, y = int(im.width * cx - e.width / 2), int(im.height * cy - e.height / 2)
        im.alpha_composite(sombra, (x + 3, y + 4))
        im.alpha_composite(e, (x, y))
    im = im.convert("RGB")
    lado = min(im.size)
    im = im.crop(((im.width - lado) // 2, 0, (im.width + lado) // 2, lado)).resize((400, 400), Image.LANCZOS)
    im.save(destino, "WEBP", quality=82)
    m["foto"] = {"url": f"https://raw.githubusercontent.com/tudosobrepaulistas/tsp-dados/main/api/figurinhas/{mid}.webp",
                 "credito": "Montagem com IA (ilustrativa) · TSP", "fonte": ref, "ia": True}
    tsp.gravar(ARQ, b)
    print(f"OK: figurinha de {m['jogador']} gravada ({destino.name})")


def cmd_validar(a):
    tm, pl = tsp.times(), paulistas()
    erros = 0
    vistos = set()
    for m in base()["itens"]:
        e = checar(m, tm, pl)
        if m["id"] in vistos:
            e.append("id repetido")
        vistos.add(m["id"])
        if e:
            erros += 1
            print(f"ERRO {m['id']}: " + "; ".join(e))
    print("Mercado OK" if not erros else f"{erros} erro(s)")
    if erros:
        sys.exit(1)


if __name__ == "__main__":
    c, resto = (sys.argv[1], sys.argv[2:]) if len(sys.argv) > 1 else ("", [])
    {"registrar": cmd_registrar, "remover": cmd_remover, "listar": cmd_listar, "gerar": cmd_gerar,
     "validar": cmd_validar, "figurinhas": cmd_figurinhas, "figurinha": cmd_figurinha}.get(c, lambda a: print(__doc__))(resto)
