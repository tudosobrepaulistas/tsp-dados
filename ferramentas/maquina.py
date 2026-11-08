#!/usr/bin/env python3
"""Máquina de Notícias TSP (Paulistão A4 com prioridade + futebol feminino + 41 clubes sem divisão / Segunda Divisão).

  python3 ferramentas/maquina.py proximo
      Mostra o próximo horário livre (08h às 23h59, de 1h30 em 1h30) e os clubes sugeridos para ele:
      os que estão há mais tempo sem matéria no site e sem matéria recente da Máquina (sorteio entre os 6 mais esquecidos).
      Também lista as últimas matérias da Máquina sobre esses clubes (para não repetir assunto).
  python3 ferramentas/maquina.py historico CLUBE
      Títulos e palavras-chave já usados para o clube (site + Máquina), para não repetir pauta nem canibalizar busca.
  python3 ferramentas/maquina.py adicionar ARQUIVO.json
      Valida a matéria e grava na fila (maquina/fila/, codificada para o Google não indexar o texto antes do site).
      O site importa em até 15 minutos e publica no horário (publish_at). Sem foto: vai como rascunho para um redator.
  python3 ferramentas/maquina.py sem-pauta CLUBE --motivo "texto" [--sugestao "pauta para o redator"]
      Registra que não achou notícia confirmada nem tema histórico seguro (aparece no painel do site).
  python3 ferramentas/maquina.py clube CLUBE --cidade X --site URL --jornais "URL1, URL2" [--redes "URL, URL"]
      Guarda as fontes de um clube em maquina/clubes.json (preencha na 1ª vez que pesquisar o clube).
  python3 ferramentas/maquina.py posjogo-pendentes
      Jogos da base que terminaram (início + 1h50) nas últimas 30 horas e ainda não têm matéria pós-jogo.
      Se não houver nenhum, mostra "nenhum" e a execução pode terminar.
  python3 ferramentas/maquina.py avisar-site
      Pede ao site para ler a fila na hora (usado depois do push de um pós-jogo).
  python3 ferramentas/maquina.py limpar
      Apaga da fila os arquivos com mais de 3 dias (já importados pelo site).

Formato da matéria (ARQUIVO.json): veja diretrizes/maquina.md.
"""
import base64
import datetime
import gzip
import hashlib
import json
import random
import re
import sys
import unicodedata
import urllib.error
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
M = RAIZ / "maquina"
FILA = M / "fila"
BR = datetime.timezone(datetime.timedelta(hours=-3))
SITE = "https://tudosobrepaulista.com.br/wp-json/wp/v2/"
PROIBIDO = re.compile(r"\b(bets?|odds?|palpites?|casas? de apostas?|bet365|betano|sportingbet|aposte)\b", re.I)
FONTE_PROIBIDA = re.compile(r"sofascore|flashscore|ogol\.|transfermarkt|fotmob|google\.com/search", re.I)
FOTO_OK = re.compile(r"^https://(upload\.wikimedia\.org|live\.staticflickr\.com|farm\d+\.staticflickr\.com|i\.ytimg\.com|[a-z0-9.-]+\.(com|com\.br|org|org\.br|net|net\.br|br))/", re.I)


def agora():
    return datetime.datetime.now(BR)


def ler(p, padrao):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return padrao


def gravar(p, d):
    Path(p).write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def clubes():
    return ler(M / "clubes.json", {"clubes": []})


def achar_clube(slug):
    for c in clubes()["clubes"]:
        if c["slug"] == slug:
            return c
    raise SystemExit(f"ERRO: clube '{slug}' não está na fase atual (maquina/clubes.json)")


def baixar(url):
    req = urllib.request.Request(url, headers={"User-Agent": "TSP-Maquina/1.0"})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.loads(r.read().decode("utf-8"))


_TERMOS = None


def termos():
    global _TERMOS
    if _TERMOS is None:
        _TERMOS = {}
        for p in (1, 2, 3):
            try:
                for t in baixar(f"{SITE}times?per_page=100&page={p}&_fields=id,slug"):
                    _TERMOS[t["slug"]] = t["id"]
            except Exception:  # noqa: BLE001
                break
    return _TERMOS


def materias_site(slug, n=20):
    tid = termos().get(slug)
    if not tid:
        return []
    out = []
    for tipo in ("materia", "posts"):
        try:
            out += baixar(f"{SITE}{tipo}?times={tid}&per_page={n}&_fields=date,title,link")
        except Exception:  # noqa: BLE001
            pass
    out.sort(key=lambda x: x["date"], reverse=True)
    return out[:n]


def historico():
    return ler(M / "historico.json", {"itens": []})


def slots_ocupados():
    return {i["publish_at"] for i in historico()["itens"] if i.get("tipo") != "posjogo"}


def proximo_slot():
    hs = clubes().get("horarios", [])
    ocup = slots_ocupados()
    t = agora() + datetime.timedelta(minutes=10)
    for dia in range(0, 3):
        d = (t + datetime.timedelta(days=dia)).date()
        for h in hs:
            hh, mm = map(int, h.split(":"))
            s = datetime.datetime(d.year, d.month, d.day, hh, mm, tzinfo=BR)
            k = s.strftime("%Y-%m-%d %H:%M")
            if s > t and k not in ocup:
                return k
    return ""


COTA = {"a4": 8, "sem_divisao": 8, "feminino": 8}


def cota_do_dia(dia):
    cont = {g: 0 for g in COTA}
    for i in historico()["itens"]:
        if i.get("tipo") != "posjogo" and not i.get("pedido") and i["publish_at"][:10] == dia:
            g = grupo_de(i["clube"])
            if g in cont:
                cont[g] += 1
    return cont


def grupo_de(slug):
    for x in clubes()["clubes"]:
        if x["slug"] == slug:
            return x.get("grupo", "")
    return ""


def cmd_proximo(_a):
    slot = proximo_slot()
    h = historico()["itens"]
    ult_maquina = {}
    for i in h:
        ult_maquina[i["clube"]] = max(ult_maquina.get(i["clube"], ""), i["publish_at"])
    linhas = []
    for c in clubes()["clubes"]:
        ms = materias_site(c["slug"], 1)
        ult = ms[0]["date"][:16].replace("T", " ") if ms else "0000"
        ult = max(ult, ult_maquina.get(c["slug"], ""))
        linhas.append((ult, c))
    linhas.sort(key=lambda x: x[0])
    # Cota diária (07/11/2026): 8 da A4, 8 sem divisão e 8 do feminino. Sugere primeiro o grupo mais atrasado no dia do horário livre.
    dia_slot = (slot or agora().strftime("%Y-%m-%d"))[:10]
    cont = cota_do_dia(dia_slot)
    grupos = sorted([g for g in COTA if cont[g] < COTA[g]], key=lambda g: cont[g] - COTA[g])
    candidatos = []
    for g in grupos:
        lista = [x for x in linhas if x[1].get("grupo") == g][:4]
        random.shuffle(lista)
        candidatos += lista[:2 if len(grupos) > 1 else 6]
    candidatos = candidatos[:6]
    print(f"Cota de {dia_slot}: A4 {cont['a4']}/8 · sem divisão {cont['sem_divisao']}/8 · feminino {cont['feminino']}/8" + ("" if grupos else " → COTA DO DIA COMPLETA"))
    print(f"Próximo horário livre: {slot or '(nenhum nas próximas 48h)'}")
    print("Clubes sugeridos (dos grupos que ainda não bateram a cota do dia; os mais esquecidos; use o 1º, se não houver pauta passe para o próximo):")
    for ult, c in candidatos:
        print(f"- {c['slug']} | {c['nome']} | { {'a4': 'A4', 'feminino': 'feminino'}.get(c.get('grupo'), 'sem divisão') } | última matéria: {ult if ult != '0000' else 'nunca'} | cidade: {c['cidade'] or '?'} | site: {c['site_oficial'] or '?'}")
    hoje = agora().strftime("%Y-%m-%d")
    feitos = [i for i in h if i["publish_at"].startswith(hoje)]
    futuros = sorted(i["publish_at"] for i in h if i["publish_at"] > agora().strftime("%Y-%m-%d %H:%M"))
    print(f"\nEstoque agendado à frente: {len(futuros)} matéria(s)" + (f" (até {futuros[-1]})" if futuros else ""))
    print(f"Máquina hoje: {len(feitos)} matéria(s): " + ", ".join(f"{i['publish_at'][11:]} {i['clube']}" for i in feitos))
    sd = [i for i in feitos if grupo_de(i["clube"]) == "sem_divisao"]
    ev = [i for i in feitos if i.get("tipo") == "historia"]
    print(f"Evergreen hoje: {len(ev)} de no máximo 4 (cota diária: 8 A4, 8 sem divisão, 8 feminino)")


def cmd_historico(a):
    slug = a[0]
    c = achar_clube(slug)
    print(f"== {c['nome']} ({slug}) | cidade: {c['cidade']} | site: {c['site_oficial']} | jornais: {', '.join(c['jornais_locais'])}")
    print("Matérias no site (mais recentes):")
    for m in materias_site(slug, 25):
        print(f"- {m['date'][:10]} | {re.sub('<[^>]+>', '', m['title']['rendered'])} | {m['link']}")
    print("Matérias da Máquina (título | palavra-chave | tipo):")
    for i in historico()["itens"]:
        if i["clube"] == slug:
            print(f"- {i['publish_at'][:10]} | {i['titulo']} | {i['foco']} | {i['tipo']}")


def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    return re.sub(r"[^a-z0-9 ]", "", "".join(ch for ch in s if unicodedata.category(ch) != "Mn"))


def cmd_adicionar(a):
    it = json.loads(Path(a[0]).read_text(encoding="utf-8"))
    erros = []
    posjogo = it.get("tipo") == "posjogo"
    if posjogo:
        c, erro_pj = checar_posjogo(it)
        erros += erro_pj
    else:
        c = achar_clube(it.get("clube", ""))
    for k in ("titulo", "subtitulo", "corpo", "resumo", "faq", "meta_title", "meta_desc", "foco", "tags", "fontes", "tipo"):
        if not it.get(k):
            erros.append(f"falta '{k}'")
    if it.get("tipo") not in ("noticia", "historia", "coletiva", "posjogo"):
        erros.append("tipo: noticia, historia, coletiva ou posjogo")
    if len(it.get("titulo", "")) > 100 or len(it.get("meta_title", "")) > 65 or len(it.get("meta_desc", "")) > 160:
        erros.append("titulo (100), meta_title (65) ou meta_desc (160) longos demais")
    if not posjogo and c["nome"].split()[0].lower() not in norm(it.get("titulo", "")) and norm(c["nome"]).split()[0] not in norm(it.get("titulo", "")):
        erros.append("o nome do clube precisa estar no título")
    corpo = it.get("corpo", [])
    if sum(1 for b in corpo if b.get("p")) < 5:
        erros.append("corpo precisa de pelo menos 5 parágrafos")
    if not any(b.get("h2") for b in corpo):
        erros.append("corpo precisa de 1 a 3 intertítulos (h2) em forma de pergunta")
    for b in corpo:
        if not (isinstance(b, dict) and len(b) == 1 and list(b)[0] in ("p", "h2", "citacao")):
            erros.append(f"bloco mal formado {b!r}")
    if not (3 <= len(it.get("faq", [])) <= 5):
        erros.append("faq: 3 a 5 perguntas")
    fontes = it.get("fontes", [])
    if it.get("tipo") in ("noticia", "posjogo") and len({f.get("url") for f in fontes}) < 2:
        erros.append("notícia precisa de 2 fontes independentes")
    if it.get("tipo") in ("historia", "coletiva") and len(fontes) < 1:
        erros.append("precisa de fonte")
    for f in fontes:
        if not str(f.get("url", "")).startswith("https://") or FONTE_PROIBIDA.search(f.get("url", "")):
            erros.append(f"fonte inválida/proibida: {f}")
        elif len(re.sub(r"^https://[^/]+/?", "", f["url"]).strip("/")) < 3:
            erros.append(f"fonte precisa ser o link da matéria/post exato, não a página inicial: {f['url']}")
        if not f.get("nome"):
            erros.append(f"fonte sem nome do veículo: {f.get('url')}")
    foto = it.get("foto") or {}
    if not posjogo and not foto:
        erros.append("foto obrigatória (07/11/2026): sem foto real com crédito a matéria não entra; procure foto do clube ou passe para outro clube")
    pedido = bool(it.get("pedido"))  # matéria pedida pelo Thiago: fora da cota e dos limites de evergreen
    if not posjogo and not pedido and c.get("grupo") in COTA:
        dia_c = (it.get("publish_at") or proximo_slot())[:10]
        if cota_do_dia(dia_c)[c["grupo"]] >= COTA[c["grupo"]]:
            erros.append(f"a cota de {dia_c} para este grupo ({COTA[c['grupo']]} matérias) já está completa: escolha um clube de outro grupo")
    if foto:
        if not FOTO_OK.match(foto.get("url", "")):
            erros.append("foto.url precisa ser https de site permitido")
        if not foto.get("credito") or not foto.get("fonte"):
            erros.append("foto precisa de credito e fonte (página de onde veio)")
    if PROIBIDO.search(json.dumps(it, ensure_ascii=False)):
        erros.append("conteúdo de aposta não pode")
    h = historico()["itens"]
    nt = norm(it.get("titulo", ""))
    for i in h:
        if i["clube"] == c["slug"] and (norm(i["titulo"]) == nt or norm(i["foco"]) == norm(it.get("foco", ""))):
            erros.append(f"repetido: já existe '{i['titulo']}' (foco '{i['foco']}')")
    if it.get("tipo") == "historia" and not pedido:
        dia = (it.get("publish_at") or proximo_slot())[:10]
        hist_dia = [i for i in h if i.get("tipo") == "historia" and not i.get("pedido") and i["publish_at"][:10] == dia]
        sd_dia = [i for i in hist_dia if grupo_de(i["clube"]) == "sem_divisao"]
        # Evergreen: até 4 por dia no total (3 de clubes sem divisão, que quase não têm notícia fora da temporada, e 1 dos demais)
        if (c.get("grupo") == "sem_divisao" and len(sd_dia) >= 3) or (c.get("grupo") != "sem_divisao" and len(hist_dia) - len(sd_dia) >= 1) or len(hist_dia) >= 4:
            erros.append(f"já há {len(hist_dia)} matérias evergreen para {dia} (máximo 3 de clubes sem divisão + 1 dos demais, para não ficar repetitivo): "
                         "use `sem-pauta CLUBE --motivo ... --sugestao ...` pedindo uma pauta à redação e passe ao próximo clube")
        lim = (agora() - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
        if any(i["clube"] == c["slug"] and i.get("tipo") == "historia" and not i.get("pedido") and i["publish_at"] >= lim for i in h):
            erros.append("este clube já teve matéria histórica nos últimos 30 dias: peça uma pauta com `sem-pauta` em vez de outra história")
    if posjogo:
        slot = agora().strftime("%Y-%m-%d %H:%M")
        if any(i.get("jogo") == it["jogo"] for i in h):
            erros.append("este jogo já tem matéria pós-jogo")
    else:
        slot = it.get("publish_at") or proximo_slot()
        if slot in {i["publish_at"] for i in h if i.get("tipo") != "posjogo"}:
            erros.append(f"horário {slot} já ocupado; use `proximo`")
    if erros:
        raise SystemExit("ERRO:\n" + "\n".join(erros))
    it["publish_at"] = slot
    it["fase"] = clubes().get("fase", 1)
    it["id"] = "m" + hashlib.md5((c["slug"] + it["titulo"]).encode()).hexdigest()[:12]
    FILA.mkdir(parents=True, exist_ok=True)
    z = base64.b64encode(gzip.compress(json.dumps(it, ensure_ascii=False).encode("utf-8"))).decode()
    nome = f"{slot.replace('-', '').replace(' ', '-').replace(':', '')}-{c['slug']}.json"
    gravar(FILA / nome, {"v": 1, "id": it["id"], "publish_at": slot, "z": z})
    escrever_indice()
    d = historico()
    d["itens"].append({"id": it["id"], "clube": c["slug"], "titulo": it["titulo"], "foco": it["foco"], "tipo": it["tipo"], "publish_at": slot, "foto": bool(foto) or bool(it.get("foto_do_jogo")), "jogo": it.get("jogo"), "pedido": pedido or None})
    d["itens"] = d["itens"][-2000:]
    gravar(M / "historico.json", d)
    print(f"OK: {nome} na fila para {slot} ({'com foto' if foto or it.get('foto_do_jogo') else 'SEM foto: vai como rascunho para um redator'})")
    if posjogo:
        print("Agora: commit + push e depois `python3 ferramentas/maquina.py avisar-site` (publica em ~1 minuto).")


def escrever_indice():
    arqs = sorted(f.name for f in FILA.glob("*.json") if f.name != "indice.json")[-60:]
    gravar(FILA / "indice.json", {"gerado": agora().isoformat(timespec="minutes"), "arquivos": arqs})


def base_jogos():
    sys.path.insert(0, str(RAIZ / "ferramentas"))
    import tsp  # noqa: E402
    return tsp


def checar_posjogo(it):
    """Confere o pós-jogo contra a base: jogo encerrado, placar no título/subtítulo, times certos."""
    tsp = base_jogos()
    erros = []
    try:
        comp, _d, j = tsp.achar(it.get("jogo", 0))
    except SystemExit as e:
        return {"slug": "", "nome": ""}, [str(e)]
    tm = tsp.times()
    casa, fora = tm.get(j["casa"], {}), tm.get(j["fora"], {})
    if j["status"] != "encerrado" or j["gols_casa"] is None:
        erros.append("o jogo ainda não está encerrado na base: registre o resultado com `tsp.py resultado` (2 fontes) antes")
    else:
        alvo = norm(it.get("titulo", "") + " " + it.get("subtitulo", ""))
        gc, gf = j["gols_casa"], j["gols_fora"]
        if not any(x in alvo for x in (f"{gc} a {gf}", f"{gf} a {gc}", f"{gc}x{gf}", f"{gc} x {gf}")):
            erros.append(f"o placar {gc}x{gf} precisa aparecer no título ou subtítulo (ex.: '{gc} a {gf}')")
    # Botafogo do Rio sempre identificado, para o leitor paulista não confundir com o Botafogo-SP
    if "botafogo" in (j["casa"], j["fora"]):
        tt = norm(it.get("titulo", ""))
        if "botafogo" in tt and not any(x in tt for x in ("botafogo rj", "botafogorj", "botafogo do rio", "alvinegro carioca")):
            erros.append("Botafogo do Rio: escreva 'Botafogo-RJ' no título (o leitor do TSP pensa no Botafogo-SP)")
    slug = it.get("clube") or casa.get("slug_tsp") or fora.get("slug_tsp") or ""
    it["clube"] = slug
    it["clubes"] = list(dict.fromkeys([x for x in (casa.get("slug_tsp"), fora.get("slug_tsp"), it.get("clube")) if x]))
    it["competicao"] = comp
    return {"slug": slug or f"jogo-{j['id']}", "nome": casa.get("nome", "")}, erros


def cmd_posjogo_pendentes(_a):
    tsp = base_jogos()
    tm = tsp.times()
    feitos = {i.get("jogo") for i in historico()["itens"] if i.get("tipo") == "posjogo"}
    t = agora()
    out = []
    for comp, j in tsp.todos_os_jogos():
        ini = datetime.datetime.fromisoformat(j["data"])
        fim = ini + datetime.timedelta(minutes=110)
        if fim <= t <= ini + datetime.timedelta(hours=30) and j["id"] not in feitos and j["status"] not in ("adiado", "cancelado"):
            out.append((ini, comp, j))
    if not out:
        print("nenhum")
        return
    for ini, comp, j in sorted(out, key=lambda x: x[0]):
        c, f = tm.get(j["casa"], {}).get("nome", j["casa"]), tm.get(j["fora"], {}).get("nome", j["fora"])
        pl = f"{j['gols_casa']}x{j['gols_fora']}" if j["gols_casa"] is not None else "SEM RESULTADO"
        print(f"- jogo {j['id']} | {comp} rodada {j['rodada'] or j['fase']} | {ini:%d/%m %H:%M} | {c} {pl} {f} | {j['status']} | {j['estadio']}")


def cmd_avisar_site(_a):
    try:
        req = urllib.request.Request("https://tudosobrepaulista.com.br/wp-json/tsp/v1/maquina-ler?x=" + str(int(agora().timestamp())), headers={"User-Agent": "TSP-Maquina/1.0"})
        with urllib.request.urlopen(req, timeout=60) as r:
            print("site:", r.read().decode()[:300])
    except urllib.error.HTTPError as e:
        print("site respondeu", e.code, "(o site lê a fila sozinho em até 15 min)")
    except Exception as e:  # noqa: BLE001
        print("não consegui avisar o site:", e, "(o site lê a fila sozinho em até 15 min)")


def opc(a, n, p=""):
    return a[a.index(n) + 1] if n in a and a.index(n) + 1 < len(a) else p


def cmd_sem_pauta(a):
    c = achar_clube(a[0])
    av = ler(RAIZ / "api" / "maquina-avisos.json", {"avisos": []})
    av["avisos"].append({"clube": c["slug"], "nome": c["nome"], "quando": agora().isoformat(timespec="minutes"), "motivo": opc(a, "--motivo"), "sugestao": opc(a, "--sugestao")})
    av["avisos"] = av["avisos"][-60:]
    av["gerado"] = agora().isoformat(timespec="minutes")
    gravar(RAIZ / "api" / "maquina-avisos.json", av)
    print(f"OK: aviso registrado para {c['nome']}")


def cmd_clube(a):
    d = clubes()
    for c in d["clubes"]:
        if c["slug"] == a[0]:
            if opc(a, "--cidade"):
                c["cidade"] = opc(a, "--cidade")
            if opc(a, "--site"):
                c["site_oficial"] = opc(a, "--site")
            if opc(a, "--jornais"):
                c["jornais_locais"] = [x.strip() for x in opc(a, "--jornais").split(",") if x.strip()]
            if opc(a, "--redes"):
                c["redes"] = [x.strip() for x in opc(a, "--redes").split(",") if x.strip()]
            gravar(M / "clubes.json", d)
            print(f"OK: {c['nome']} atualizado")
            return
    raise SystemExit("ERRO: clube não encontrado")


def cmd_limpar(_a):
    lim = (agora() - datetime.timedelta(days=3)).strftime("%Y%m%d")
    n = 0
    for f in FILA.glob("*.json"):
        if f.name != "indice.json" and f.name[:8] < lim:
            f.unlink()
            n += 1
    escrever_indice()
    print(f"OK: {n} arquivo(s) antigos apagados")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    {"proximo": cmd_proximo, "historico": cmd_historico, "adicionar": cmd_adicionar, "sem-pauta": cmd_sem_pauta,
     "clube": cmd_clube, "limpar": cmd_limpar,
     "posjogo-pendentes": cmd_posjogo_pendentes, "avisar-site": cmd_avisar_site}.get(cmd, lambda a: print(__doc__))(sys.argv[2:])
