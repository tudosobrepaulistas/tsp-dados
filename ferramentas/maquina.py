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
  python3 ferramentas/maquina.py versoes-pendentes [--horas 36]
      Matérias de redatores com 2 ou mais clubes paulistas marcados e as versões por clube que faltam (diretrizes/versoes.md).
  python3 ferramentas/maquina.py cobertura-6h
      Clubes paulistas das Séries A e B sem matéria no site há 6h ou mais (a Máquina cobre: diretrizes/cobertura.md).
  python3 ferramentas/maquina.py original ID
      Texto limpo da matéria original (para escrever a versão).
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
import html
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
    return {i["publish_at"] for i in historico()["itens"] if i.get("tipo") not in ("posjogo", "video", "versao")}


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
        if i.get("tipo") not in ("posjogo", "video", "versao") and not i.get("pedido") and i["publish_at"][:10] == dia:
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


MAQ_AUTORES = {3, 39}  # Máquina e Redação TSP: matérias delas não geram versões


def termos_times(ids):
    if not ids:
        return {}
    url = "https://tudosobrepaulista.com.br/wp-json/wp/v2/times?per_page=100&_fields=id,slug,name&include=" + ",".join(str(i) for i in ids)
    return {t["id"]: t for t in baixar(url)}


def cmd_versoes_pendentes(a):
    horas = int(a[a.index("--horas") + 1]) if "--horas" in a else 36
    depois = (agora() - datetime.timedelta(hours=horas)).strftime("%Y-%m-%dT%H:%M:%S")
    ms = baixar(f"https://tudosobrepaulista.com.br/wp-json/wp/v2/materia?after={depois}&per_page=100&_fields=id,date,author,times,title,link")
    feitos = {(i.get("versao_de"), i["clube"]) for i in historico()["itens"] if i.get("tipo") == "versao"}
    ms = [m for m in ms if m["author"] not in MAQ_AUTORES and len(m.get("times") or []) >= 2]
    tt = termos_times(sorted({t for m in ms for t in m["times"]}))
    total = 0
    for m in sorted(ms, key=lambda x: x["date"]):
        tit = re.sub("<[^>]+>", "", m["title"]["rendered"])
        nt = norm(tit)
        clubes_m = [tt[t] for t in m["times"] if t in tt]
        pos = sorted(clubes_m, key=lambda c: (nt.find(norm(c["name"])) if norm(c["name"]) in nt else 9999))
        principal = pos[0]
        faltam = [c for c in clubes_m if c["id"] != principal["id"] and (m["id"], c["slug"]) not in feitos]
        if not faltam:
            continue
        total += len(faltam)
        print(f"- matéria {m['id']} | {m['date'][:16]} | {tit}")
        print(f"  {m['link']}")
        print(f"  ótica original: {principal['name']} ({principal['slug']}) | versões que faltam: " + ", ".join(f"{c['name']} ({c['slug']})" for c in faltam))
    print(f"\n{total} versão(ões) pendente(s)." if total else "nenhuma")


def checar_citacoes(corpo):
    """Boas práticas (08/11/2026): fonte vai no rodapé (campo fontes), não repetida no texto."""
    txt = " ".join(str(b.get("p", "")) for b in corpo if isinstance(b, dict))
    t = _sem_acento(txt)
    e = []
    if re.search(r"(tambem foi confirmad|confirmad[oa]s? (tambem )?(por|pelo|pela)|duas fontes|fontes consultadas|segundo as fontes|de acordo com as fontes|checad[oa] (em|com))", t):
        e.append("não escreva sobre a checagem no texto ('confirmado também por X', 'duas fontes'): as fontes já aparecem no rodapé da matéria")
    n = len(re.findall(r"\b(segundo (o|a|os|as)|de acordo com (o|a)|conforme (o|a|publicou|informou)|informou (o|a)|publicou (o|a)|apurou (o|a)|divulgou (o|a))\b", t))
    if n > 2:
        e.append(f"excesso de atribuição no texto ({n}x 'segundo o/de acordo com'): cite o veículo só se a informação for exclusiva dele ou se ele for parte da notícia; nota oficial e coletiva: 'em nota', 'na coletiva', uma vez")
    return e


def _sem_acento(t):
    import unicodedata
    return "".join(ch for ch in unicodedata.normalize("NFD", t.lower()) if unicodedata.category(ch) != "Mn")


def checar_mostra(foto, titulo, nome_clube):
    """Critério de foto (08/11/2026): a foto tem que mostrar exatamente o assunto da matéria."""
    m = _sem_acento(foto.get("mostra", ""))
    t = _sem_acento(titulo)
    if len(m) < 25:
        return ["foto.mostra obrigatório: descreva em uma frase o que a foto mostra (quem, qual jogo/momento, quando). Ex.: \"Jogadores do Novorizontino e do Criciúma disputam bola no Jorjão, 21/07/2026\""]
    e = []
    palavras = [w for w in re.findall(r"[a-z]{4,}", _sem_acento(nome_clube)) if w not in ("clube", "esporte", "futebol", "associacao", "atletico", "sport", "feminino")]
    if palavras and not any(w in m for w in palavras):
        e.append(f"foto.mostra precisa citar o clube ({nome_clube}): a foto tem que ser do clube da matéria")
    if re.search(r"titulo|campe|acesso|conquist", t) and not re.search(r"decid|busca|pode |briga|sonha|disputa|rumo|luta|vai |precisa|chance", t) and not re.search(r"titulo|campe|taca|trofeu|comemor|festa|acesso|conquist", m):
        e.append("matéria de título/acesso/conquista: a foto tem que ser da conquista (taça, comemoração), não foto genérica")
    if re.search(r" x |contra |decide|enfrenta|duelo|jogo|partida|rodada", t) and not re.search(r" x |jogo|partida|lance|disputa|gol|rodada|campo|treino|escala", m) and not re.search(r"titulo|campe|comemor", m):
        e.append("matéria de jogo: a foto tem que ser de jogo (de preferência entre os mesmos times), não retrato, estádio vazio ou arte")
    if re.search(r"\barte\b|logo|escudo|montagem|card |banner", m):
        e.append("arte, escudo, logo ou montagem não servem como foto principal")
    return e


def cmd_lixeira(a):
    """lixeira MAQ_ID: manda para a lixeira o RASCUNHO dessa matéria da Máquina (publicada não é tocada)."""
    alvo = a[0]
    slot = agora().strftime("%Y-%m-%d %H:%M")
    it = {"id": "x" + hashlib.md5(alvo.encode()).hexdigest()[:12], "tipo": "lixeira", "alvo": alvo}
    z = base64.b64encode(gzip.compress(json.dumps(it).encode("utf-8"))).decode()
    nome = f"{slot.replace('-', '').replace(' ', '-').replace(':', '')}-lixeira-{alvo}.json"
    gravar(FILA / nome, {"v": 1, "id": it["id"], "publish_at": slot, "z": z})
    escrever_indice()
    print(f"OK: {nome}. Commit, push e avisar-site.")


def cmd_trocar_foto(a):
    alvo = a[0]
    def opt(n):
        return a[a.index(n) + 1] if n in a else ""
    foto = {"url": opt("--url"), "credito": opt("--credito"), "fonte": opt("--fonte"), "alt": opt("--alt"), "mostra": opt("--mostra")}
    if not FOTO_OK.match(foto["url"]) or not foto["credito"] or not foto["fonte"]:
        raise SystemExit("ERRO: --url (https), --credito, --fonte e --mostra são obrigatórios")
    h = next((i for i in historico()["itens"] if i["id"] == alvo), None)
    cl = next((k for k in json.loads((RAIZ / "maquina" / "clubes.json").read_text(encoding="utf-8"))["clubes"] if h and k["slug"] == h.get("clube")), {})
    err = checar_mostra(foto, (h or {}).get("titulo", ""), cl.get("nome", ""))
    if err:
        raise SystemExit("ERRO:\n" + "\n".join(err))
    if not any(i["id"] == alvo for i in historico()["itens"]):
        raise SystemExit(f"ERRO: matéria {alvo} não está no histórico da Máquina")
    slot = agora().strftime("%Y-%m-%d %H:%M")
    it = {"id": "f" + hashlib.md5((alvo + foto["url"]).encode()).hexdigest()[:12], "tipo": "troca_foto", "alvo": alvo, "foto": foto}
    z = base64.b64encode(gzip.compress(json.dumps(it, ensure_ascii=False).encode("utf-8"))).decode()
    nome = f"{slot.replace('-', '').replace(' ', '-').replace(':', '')}-foto-{alvo}.json"
    gravar(FILA / nome, {"v": 1, "id": it["id"], "publish_at": slot, "z": z})
    escrever_indice()
    print(f"OK: troca de foto na fila ({nome}). Commit, push e avisar-site.")


BLOCOS = {"A1": ["botafogosp", "capivariano", "corinthians", "ferroviaria", "guarani", "juventus", "mirassol", "noroeste", "novorizontino", "palmeiras", "portuguesa", "primavera", "bragantino", "santos", "saobernardo", "saopaulo"], "A2": ["aguasanta", "interdelimeira", "ituano", "linense", "marilia", "monteazul", "osasco-sporting", "pontepreta", "portuguesasantista", "santoandre", "saojose", "sertaozinho", "taubate", "veloclube", "votuporanguense", "xvdepiracicaba"], "A3": ["bandeirante", "catanduva", "ec-sao-bernardo", "francana", "prudente", "inter-de-bebedouro", "itapirense", "paulista-jundiai", "penapolense", "rio-branco", "rioclaro", "rio-preto", "saobento", "uniao-barbarense", "uniao-sao-joao", "xv-de-jau"]}


def ultima_materia_de(slugs):
    """Matéria mais recente do site entre os clubes (slugs da classificação Times): (horas, título, data)."""
    ts = baixar("https://tudosobrepaulista.com.br/wp-json/wp/v2/times?per_page=100&_fields=id,slug&slug=" + ",".join(slugs))
    ids = [str(t["id"]) for t in ts]
    if not ids:
        return 999, "(nenhuma)"
    ms = baixar("https://tudosobrepaulista.com.br/wp-json/wp/v2/materia?per_page=1&_fields=date,title&times=" + ",".join(ids))
    if not ms:
        return 999, "(nenhuma)"
    d = datetime.datetime.fromisoformat(ms[0]["date"]).replace(tzinfo=BR)
    return (agora() - d).total_seconds() / 3600, re.sub("<[^>]+>", "", ms[0]["title"]["rendered"])


def pautas_de(slugs):
    try:
        d = json.loads((RAIZ / "api" / "pautas.json").read_text(encoding="utf-8"))
    except Exception:  # noqa
        return []
    lim = (agora() - datetime.timedelta(hours=48)).strftime("%Y-%m-%dT%H:%M")
    return [x for x in d.get("itens", []) if x.get("clube") in slugs and str(x.get("gerado") or x.get("quando") or "") >= lim]


def cmd_cobertura(a):
    """Clubes paulistas das Séries A e B sem matéria no site há 6 horas ou mais."""
    limite = float(a[a.index("--horas") + 1]) if "--horas" in a else 6
    t = agora()
    out = []
    for c in clubes()["clubes"]:
        if c.get("grupo") != "nacional":
            continue
        ms = materias_site(c["slug"], 1)
        if ms:
            d = datetime.datetime.fromisoformat(ms[0]["date"]).replace(tzinfo=BR)
            h = (t - d).total_seconds() / 3600
            tit = re.sub("<[^>]+>", "", ms[0]["title"]["rendered"])
        else:
            h, tit = 999, "(nenhuma)"
        if h >= limite:
            out.append((h, c, tit))
    # Blocos da home do Paulistão A1, A2 e A3 (redação): das 8h às 23h59, nenhum bloco fica 6h sem matéria nova
    nac = {c["slug"] for c in clubes()["clubes"] if c.get("grupo") == "nacional"}
    blocos = []
    if 8 <= t.hour <= 23:
        for nome, slugs in BLOCOS.items():
            sl = [x for x in slugs if x not in nac]
            h, tit = ultima_materia_de(sl)
            if h >= limite:
                esquec = []
                for x in sl:
                    hx, _ = ultima_materia_de([x])
                    esquec.append((hx, x))
                esquec.sort(reverse=True)
                blocos.append((nome, h, tit, [x for _, x in esquec[:4]], pautas_de(sl)))
    for h, c, tit in sorted(out, key=lambda x: -x[0]):
        print(f"- {c['slug']} | {c['nome']} ({c.get('divisao', '')}) | última matéria há {h:.1f}h: {tit}")
        for p in pautas_de([c["slug"]])[:2]:
            print(f"    pauta da redação: {p['titulo']} | fontes: " + ", ".join(f['url'] for f in p.get('fontes', [])))
    for nome, h, tit, esq, ps in blocos:
        print(f"- BLOCO Paulistão {nome} | última matéria do bloco há {h:.1f}h: {tit}")
        print(f"    clubes mais esquecidos: {', '.join(esq)} (escreva 1 matéria para o bloco, de preferência de uma pauta abaixo)")
        for p in ps[:4]:
            print(f"    pauta da redação ({p['clube']}): {p['titulo']} | fontes: " + ", ".join(f['url'] for f in p.get('fontes', [])))
    if not out and not blocos:
        print("nenhum")


def cmd_original(a):
    m = baixar(f"https://tudosobrepaulista.com.br/wp-json/wp/v2/materia/{int(a[0])}?_fields=id,date,link,title,content,times")
    import html as _h
    txt = re.sub(r"<(script|style|figure)[^>]*>.*?</\1>", " ", m["content"]["rendered"], flags=re.S)
    txt = re.sub(r"</(p|h2|h3|li|blockquote)>", "\n", txt)
    txt = _h.unescape(re.sub(r"<[^>]+>", "", txt))
    print(f"ID {m['id']} | {m['date'][:16]} | {m['link']}")
    print(_h.unescape(m["title"]["rendered"]))
    print("clubes marcados:", ", ".join(f"{t['name']} ({t['slug']})" for t in termos_times(m.get("times") or []).values()))
    print("-" * 60)
    print(re.sub(r"\n\s*\n+", "\n\n", txt).strip())


def adicionar_versao(it):
    erros = []
    for k in ("versao_de", "clube", "clube_nome", "titulo", "subtitulo", "corpo", "resumo", "foco", "meta_title", "meta_desc", "tags", "fontes"):
        if not it.get(k):
            erros.append(f"falta '{k}'")
    if sum(1 for b in it.get("corpo", []) if isinstance(b, dict) and b.get("p")) < 4:
        erros.append("corpo precisa de pelo menos 4 parágrafos")
    for b in it.get("corpo", []):
        if not (isinstance(b, dict) and len(b) == 1 and list(b)[0] in ("p", "h2", "citacao")):
            erros.append(f"bloco mal formado {b!r}")
    if len(it.get("titulo", "")) > 100 or len(it.get("meta_title", "")) > 65 or len(it.get("meta_desc", "")) > 160:
        erros.append("titulo (100), meta_title (65) ou meta_desc (160) longos demais")
    if norm(it.get("clube_nome", "x")).split()[0] not in norm(it.get("titulo", "")):
        erros.append("o nome do clube da versão precisa estar no título")
    if not any(f"tudosobrepaulista.com.br" in str(f.get("url", "")) for f in it.get("fontes", [])):
        erros.append("a 1ª fonte é a matéria original do redator (link do TSP)")
    if PROIBIDO.search(json.dumps(it, ensure_ascii=False)):
        erros.append("conteúdo de aposta não pode")
    h = historico()["itens"]
    if any(i.get("tipo") == "versao" and i.get("versao_de") == it.get("versao_de") and i["clube"] == it.get("clube") for i in h):
        erros.append("esta versão já existe")
    if erros:
        raise SystemExit("ERRO:\n" + "\n".join(erros))
    slot = agora().strftime("%Y-%m-%d %H:%M")
    it["publish_at"] = slot
    it["tipo"] = "versao"
    it["id"] = "v" + hashlib.md5(f"{it['versao_de']}-{it['clube']}".encode()).hexdigest()[:12]
    FILA.mkdir(parents=True, exist_ok=True)
    z = base64.b64encode(gzip.compress(json.dumps(it, ensure_ascii=False).encode("utf-8"))).decode()
    nome = f"{slot.replace('-', '').replace(' ', '-').replace(':', '')}-v{it['versao_de']}-{it['clube']}.json"
    gravar(FILA / nome, {"v": 1, "id": it["id"], "publish_at": slot, "z": z})
    escrever_indice()
    d = historico()
    d["itens"].append({"id": it["id"], "clube": it["clube"], "titulo": it["titulo"], "foco": it["foco"], "tipo": "versao", "publish_at": slot, "foto": True, "versao_de": it["versao_de"]})
    d["itens"] = d["itens"][-2000:]
    gravar(M / "historico.json", d)
    print(f"OK: versão de {it['clube']} da matéria {it['versao_de']} na fila ({nome}). Commit, push e avisar-site.")


def cmd_adicionar(a):
    it = json.loads(Path(a[0]).read_text(encoding="utf-8"))
    if it.get("tipo") == "versao":
        return adicionar_versao(it)
    erros = []
    posjogo = it.get("tipo") == "posjogo"
    video = it.get("tipo") == "video"
    if posjogo:
        c, erro_pj = checar_posjogo(it)
        erros += erro_pj
    elif it.get("pedido") and not any(x["slug"] == it.get("clube") for x in clubes()["clubes"]):
        # Pedido do Thiago sobre clube fora da lista da Máquina (ex.: Palmeiras): vale com o endereço do clube no site
        slug = it.get("clube", "")
        c = {"slug": slug, "nome": it.get("clube_nome") or slug.replace("-", " ").title(), "grupo": ""}
    else:
        c = achar_clube(it.get("clube", ""))
    for k in ("titulo", "subtitulo", "corpo", "resumo", "faq", "meta_title", "meta_desc", "foco", "tags", "fontes", "tipo"):
        if not it.get(k):
            erros.append(f"falta '{k}'")
    if it.get("tipo") not in ("noticia", "historia", "coletiva", "posjogo", "video"):
        erros.append("tipo: noticia, historia, coletiva, posjogo ou video")
    if video:
        v = it.get("video") or {}
        if not re.fullmatch(r"[A-Za-z0-9_-]{11}", str(v.get("id", ""))) or not v.get("canal"):
            erros.append("video: {id: 'ID de 11 letras do YouTube', canal: 'nome do canal oficial'}")
        elif any(i.get("video") == v["id"] for i in historico()["itens"]):
            erros.append("este vídeo já tem matéria")
        elif not any(v["id"] in f.get("url", "") for f in it.get("fontes", [])):
            erros.append("a 1ª fonte é o próprio vídeo (https://www.youtube.com/watch?v=ID)")
        if "youtube" not in json.dumps(it.get("foto") or {}).lower() and "ytimg" not in json.dumps(it.get("foto") or {}):
            erros.append("foto de vídeo: miniatura do próprio vídeo (i.ytimg.com/vi/ID/maxresdefault.jpg), crédito 'Foto: Reprodução/YouTube Canal'")
    if len(it.get("titulo", "")) > 100 or len(it.get("meta_title", "")) > 65 or len(it.get("meta_desc", "")) > 160:
        erros.append("titulo (100), meta_title (65) ou meta_desc (160) longos demais")
    if not posjogo and c["nome"].split()[0].lower() not in norm(it.get("titulo", "")) and norm(c["nome"]).split()[0] not in norm(it.get("titulo", "")):
        erros.append("o nome do clube precisa estar no título")
    corpo = it.get("corpo", [])
    if sum(1 for b in corpo if b.get("p")) < (4 if video else 5):
        erros.append("corpo precisa de pelo menos 5 parágrafos (vídeo: 4)")
    erros += checar_citacoes(corpo)
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
    if it.get("tipo") in ("historia", "coletiva", "video") and len(fontes) < 1:
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
    if not posjogo and not video and not pedido and c.get("grupo") in COTA:
        dia_c = (it.get("publish_at") or proximo_slot())[:10]
        if cota_do_dia(dia_c)[c["grupo"]] >= COTA[c["grupo"]]:
            erros.append(f"a cota de {dia_c} para este grupo ({COTA[c['grupo']]} matérias) já está completa: escolha um clube de outro grupo")
    if foto:
        if not FOTO_OK.match(foto.get("url", "")):
            erros.append("foto.url precisa ser https de site permitido")
        if not foto.get("credito") or not foto.get("fonte"):
            erros.append("foto precisa de credito e fonte (página de onde veio)")
        erros += checar_mostra(foto, it.get("titulo", ""), c.get("nome", ""))
    if PROIBIDO.search(json.dumps(it, ensure_ascii=False)):
        erros.append("conteúdo de aposta não pode")
    h = historico()["itens"]
    nt = norm(it.get("titulo", ""))
    for i in h:
        if i["clube"] == c["slug"] and (norm(i["titulo"]) == nt or norm(i["foco"]) == norm(it.get("foco", ""))):
            erros.append(f"repetido: já existe '{i['titulo']}' (foco '{i['foco']}')")
    efem = it.get("efemeride") or {}
    if efem:
        # "Neste dia" (08/11/2026): 1 por dia, jogo de 10, 15, 20, 25... anos atrás na mesma data, de qualquer divisão
        dia_pub = (it.get("publish_at") or proximo_slot())[:10]
        try:
            dj = datetime.date.fromisoformat(str(efem.get("data", "")))
            dp = datetime.date.fromisoformat(dia_pub)
            if (dj.month, dj.day) != (dp.month, dp.day) or (dp.year - dj.year) % 5 or dp.year - dj.year < 5:
                erros.append(f"efeméride: o jogo ({dj}) precisa ser no mesmo dia e mês da publicação ({dp}), há 5, 10, 15, 20... anos")
        except ValueError:
            erros.append("efeméride: data = 'AAAA-MM-DD' do jogo histórico")
        if it.get("tipo") != "historia" or len(fontes) < 1:
            erros.append("efeméride: tipo 'historia' com pelo menos 1 fonte (jornal da época, site oficial, FPF, Wikipédia)")
        if any(i.get("efemeride") and i["publish_at"][:10] == dia_pub for i in historico()["itens"]):
            erros.append(f"já há matéria 'Neste dia' para {dia_pub}")
    if c.get("grupo") in ("nacional", "redacao") and it.get("tipo") not in ("noticia", "coletiva", "video") and not posjogo and not pedido and not efem:
        erros.append("clube da redação (Séries A/B, A1 a A3): só notícia ou coletiva atualizada (nada de evergreen)")
    if c.get("grupo") in ("nacional", "redacao") and not it.get("publish_at"):
        it["publish_at"] = (agora() + datetime.timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M")
    if it.get("tipo") == "historia" and not pedido and not efem:
        dia = (it.get("publish_at") or proximo_slot())[:10]
        hist_dia = [i for i in h if i.get("tipo") == "historia" and not i.get("pedido") and i["publish_at"][:10] == dia]
        sd_dia = [i for i in hist_dia if grupo_de(i["clube"]) == "sem_divisao"]
        # Evergreen (08/11/2026, fora de temporada A4 e sem divisão quase não têm notícia): até 4 de sem divisão + 4 da A4 + 2 do feminino por dia
        lim_g = {"sem_divisao": 4, "a4": 4, "feminino": 2}.get(c.get("grupo"), 0)
        do_grupo = [i for i in hist_dia if grupo_de(i["clube"]) == c.get("grupo")]
        if len(do_grupo) >= lim_g:
            erros.append(f"já há {len(do_grupo)} matérias evergreen deste grupo para {dia} (máximo 4 sem divisão, 4 A4, 2 feminino): "
                         "use `sem-pauta CLUBE --motivo ... --sugestao ...` pedindo uma pauta à redação e passe ao próximo clube")
        lim = (agora() - datetime.timedelta(days=14)).strftime("%Y-%m-%d")
        if any(i["clube"] == c["slug"] and i.get("tipo") == "historia" and not i.get("pedido") and i["publish_at"] >= lim for i in h):
            erros.append("este clube já teve matéria histórica nos últimos 14 dias: peça uma pauta com `sem-pauta` em vez de outra história")
    if video:
        slot = (agora() + datetime.timedelta(minutes=3)).strftime("%Y-%m-%d %H:%M")
    elif posjogo:
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
    nome = f"{slot.replace('-', '').replace(' ', '-').replace(':', '')}-{c['slug']}{'-v' + it['video']['id'] if video else ''}.json"
    gravar(FILA / nome, {"v": 1, "id": it["id"], "publish_at": slot, "z": z})
    escrever_indice()
    d = historico()
    d["itens"].append({"id": it["id"], "clube": c["slug"], "titulo": it["titulo"], "foco": it["foco"], "tipo": it["tipo"], "publish_at": slot, "foto": bool(foto) or bool(it.get("foto_do_jogo")), "jogo": it.get("jogo"), "pedido": pedido or None, "video": (it.get("video") or {}).get("id"), "efemeride": (it.get("efemeride") or {}).get("data")})
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
    if str(comp).startswith("fem_") and it.get("clube") and it["clube"].endswith("-feminino"):
        it["clubes"] = [it["clube"]]  # feminino: só a página/bloco do time feminino, não o masculino
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


UA_YT = {"User-Agent": "Mozilla/5.0 (TSP-Maquina)"}
ENTREVISTA = re.compile(r"coletiva|entrevista|\bfala\b|falou|pronunciamento|apresentac|zona mista|exclusiv|bate-papo|papo com|conversa|declarac|apos (a )?(vitoria|derrota|empate|jogo)|pos-jogo|pre-jogo")
NAO_ENTREVISTA = re.compile(r"ao vivo com imagens|jogo completo|melhores momentos|\bgols\b|torcedor|torcida|#shorts|sorteio|promoc|loja|camisa nova|unboxing")


def _get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA_YT), timeout=30) as r:
        return r.read().decode("utf-8", "replace"), r.geturl()


def cmd_youtube_canal(a):
    """youtube-canal SLUG URL_DO_CANAL  (ex.: https://www.youtube.com/@saopaulofc). Grava o canal oficial do clube."""
    slug, url = a[0], a[1]
    html_, final = _get(url)
    m = re.search(r'https://www\.youtube\.com/channel/(UC[A-Za-z0-9_-]{22})', html_) or re.search(r'"channelId":"(UC[A-Za-z0-9_-]{22})"', html_)
    if not m:
        raise SystemExit("não achei o ID do canal nessa página")
    cid = m.group(1)
    feed, _ = _get(f"https://www.youtube.com/feeds/videos.xml?channel_id={cid}")
    nome = html.unescape(re.search(r"<title>(.*?)</title>", feed).group(1))
    datas = re.findall(r"<entry>.*?<published>(.*?)</published>", feed, re.S)
    if not datas or datas[0][:10] < (agora() - datetime.timedelta(days=60)).strftime("%Y-%m-%d"):
        raise SystemExit(f"canal '{nome}' parado (último vídeo: {datas[0][:10] if datas else 'nenhum'}): não é o canal oficial ativo; procure o link do YouTube no site oficial do clube")
    d = clubes()
    for k in d["clubes"]:
        if k["slug"] == slug:
            k["youtube"] = {"id": cid, "nome": nome, "url": final}
            gravar(M / "clubes.json", d)
            print(f"OK: {slug} → {nome} ({cid}). Confira se é o canal OFICIAL do clube.")
            return
    raise SystemExit(f"clube {slug} não está em maquina/clubes.json")


def cmd_videos(a):
    """videos [--horas 36]: vídeos novos dos canais oficiais (sem matéria ainda), do mais antigo para o mais novo."""
    horas = int(opc(a, "--horas", "36"))
    lim = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=horas)
    feitos = {i.get("video") for i in historico()["itens"] if i.get("video")}
    achados, sem = [], []
    for k in clubes()["clubes"]:
        yt = k.get("youtube")
        if not yt:
            sem.append(k["slug"])
            continue
        try:
            feed, _ = _get(f"https://www.youtube.com/feeds/videos.xml?channel_id={yt['id']}")
        except Exception as e:  # noqa: BLE001
            print(f"! {k['slug']}: feed falhou ({e})")
            continue
        for ent in re.findall(r"<entry>(.*?)</entry>", feed, re.S):
            vid = re.search(r"<yt:videoId>(.*?)</yt:videoId>", ent).group(1)
            pub = datetime.datetime.fromisoformat(re.search(r"<published>(.*?)</published>", ent).group(1))
            link = re.search(r'<link rel="alternate" href="([^"]+)"', ent).group(1)
            if pub < lim or vid in feitos or "/shorts/" in link:
                continue
            tit = html.unescape(re.search(r"<title>(.*?)</title>", ent).group(1))
            # Só entrevista/coletiva (regra de 08/11/2026): torcida, história, lives e gols ficam de fora
            if not ENTREVISTA.search(_sem_acento(tit)) or NAO_ENTREVISTA.search(_sem_acento(tit)):
                continue
            desc = html.unescape((re.search(r"<media:description>(.*?)</media:description>", ent, re.S) or re.search(r"()", "")).group(1))
            achados.append((pub, k["slug"], yt["nome"], vid, tit, desc))
    achados.sort()
    if not achados:
        print("nenhum")
    for pub, slug, canal, vid, tit, desc in achados:
        print("=" * 70)
        print(f"{slug} | canal: {canal} | {pub.astimezone(BR).strftime('%d/%m %H:%M')} | https://www.youtube.com/watch?v={vid}")
        print(f"  {tit}")
        if desc.strip():
            print("  descrição: " + re.sub(r"\s+", " ", desc)[:600])
    print("(Só entrevistas e coletivas aparecem aqui. Feminino: use o clube '<clube>-feminino'. Base: 'Sub-20', 'Sub-17'... no título.)")
    print(f"\n{len(achados)} vídeo(s) novos. Clubes sem canal cadastrado ({len(sem)}): {', '.join(sem[:60])}")


GRANDES = ("palmeiras", "corinthians", "saopaulo", "santos")


def cmd_grandes(a):
    """grandes: horas desde a última matéria de cada um dos 4 grandes (qualquer autor), o mais esquecido primeiro,
    com as pautas das últimas 24h de cada um. Regra (09/11/2026): 1 matéria dos 4 grandes a cada 1h30."""
    linhas = []
    for s in GRANDES:
        try:
            h, t = ultima_materia_de([s])
        except Exception as e:  # noqa: BLE001
            h, t = 99, f"(não consegui ler o site: {e})"
        linhas.append((h, s, t))
    linhas.sort(reverse=True)
    mais_recente = min(x[0] for x in linhas)
    print(f"Última matéria dos 4 grandes: há {mais_recente:.1f}h" + ("  → em dia (menos de 1h20), pode terminar" if mais_recente < 1.33 else "  → PUBLICAR 1 agora"))
    for h, s, t in linhas:
        print(f"- {s}: {h:.1f}h sem matéria | última: {t}")
        for p_ in pautas_de([s])[:4]:
            print(f"    pauta {p_.get('quando', '')}: {p_['titulo']} | " + " ".join(f['url'] for f in p_.get('fontes', [])))


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
     "posjogo-pendentes": cmd_posjogo_pendentes, "avisar-site": cmd_avisar_site, "versoes-pendentes": cmd_versoes_pendentes, "original": cmd_original, "trocar-foto": cmd_trocar_foto, "cobertura-6h": cmd_cobertura, "youtube-canal": cmd_youtube_canal, "videos": cmd_videos, "lixeira": cmd_lixeira, "grandes": cmd_grandes}.get(cmd, lambda a: print(__doc__))(sys.argv[2:])
