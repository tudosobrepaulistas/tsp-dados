#!/usr/bin/env python3
"""Máquina de Notícias TSP (fase 1: 41 clubes sem divisão / Segunda Divisão).

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
    return {i["publish_at"] for i in historico()["itens"]}


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
    candidatos = linhas[:6]
    random.shuffle(candidatos)
    print(f"Próximo horário livre: {slot or '(nenhum nas próximas 48h)'}")
    print("Clubes sugeridos (sorteio entre os 6 mais esquecidos; use o 1º, se não houver pauta passe para o próximo):")
    for ult, c in candidatos:
        print(f"- {c['slug']} | {c['nome']} | última matéria: {ult if ult != '0000' else 'nunca'} | cidade: {c['cidade'] or '?'} | site: {c['site_oficial'] or '?'}")
    hoje = agora().strftime("%Y-%m-%d")
    feitos = [i for i in h if i["publish_at"].startswith(hoje)]
    futuros = sorted(i["publish_at"] for i in h if i["publish_at"] > agora().strftime("%Y-%m-%d %H:%M"))
    print(f"\nEstoque agendado à frente: {len(futuros)} matéria(s)" + (f" (até {futuros[-1]})" if futuros else ""))
    print(f"Máquina hoje: {len(feitos)} matéria(s): " + ", ".join(f"{i['publish_at'][11:]} {i['clube']}" for i in feitos))


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
    c = achar_clube(it.get("clube", ""))
    for k in ("titulo", "subtitulo", "corpo", "resumo", "faq", "meta_title", "meta_desc", "foco", "tags", "fontes", "tipo"):
        if not it.get(k):
            erros.append(f"falta '{k}'")
    if it.get("tipo") not in ("noticia", "historia", "coletiva"):
        erros.append("tipo: noticia, historia ou coletiva")
    if len(it.get("titulo", "")) > 100 or len(it.get("meta_title", "")) > 65 or len(it.get("meta_desc", "")) > 160:
        erros.append("titulo (100), meta_title (65) ou meta_desc (160) longos demais")
    if c["nome"].split()[0].lower() not in norm(it.get("titulo", "")) and norm(c["nome"]).split()[0] not in norm(it.get("titulo", "")):
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
    if it.get("tipo") == "noticia" and len({f.get("url") for f in fontes}) < 2:
        erros.append("notícia precisa de 2 fontes independentes")
    if it.get("tipo") in ("historia", "coletiva") and len(fontes) < 1:
        erros.append("precisa de fonte")
    for f in fontes:
        if not str(f.get("url", "")).startswith("https://") or FONTE_PROIBIDA.search(f.get("url", "")):
            erros.append(f"fonte inválida/proibida: {f}")
    foto = it.get("foto") or {}
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
    slot = it.get("publish_at") or proximo_slot()
    if slot in {i["publish_at"] for i in h}:
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
    d["itens"].append({"id": it["id"], "clube": c["slug"], "titulo": it["titulo"], "foco": it["foco"], "tipo": it["tipo"], "publish_at": slot, "foto": bool(foto)})
    d["itens"] = d["itens"][-2000:]
    gravar(M / "historico.json", d)
    print(f"OK: {nome} na fila para {slot} ({'com foto' if foto else 'SEM foto: vai como rascunho para um redator'})")


def escrever_indice():
    arqs = sorted(f.name for f in FILA.glob("*.json") if f.name != "indice.json")[-60:]
    gravar(FILA / "indice.json", {"gerado": agora().isoformat(timespec="minutes"), "arquivos": arqs})


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
     "clube": cmd_clube, "limpar": cmd_limpar}.get(cmd, lambda a: print(__doc__))(sys.argv[2:])
