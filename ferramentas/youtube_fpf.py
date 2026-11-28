#!/usr/bin/env python3
"""Links das transmissões da Federação Paulista no YouTube (canal Paulistão, @paulistao) — regra 18 do CLAUDE.md.

  python3 ferramentas/youtube_fpf.py listar            ao vivo e programados (com link), mais os jogos completos recentes
  python3 ferramentas/youtube_fpf.py achar "Santos" "Mauaense"   link do jogo entre os dois clubes (ou nada)

Lê só a página pública de transmissões do canal (1 página por chamada). Use o link no lide e no "Onde assistir".
"""
import json
import re
import sys
import unicodedata
import urllib.request

CANAL = "https://www.youtube.com/@paulistao/streams"


def norm(s):
    s = unicodedata.normalize("NFD", s or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def videos():
    req = urllib.request.Request(CANAL, headers={"User-Agent": "Mozilla/5.0", "Accept-Language": "pt-BR",
                                                 "Cookie": "CONSENT=YES+1; SOCS=CAI"})
    h = urllib.request.urlopen(req, timeout=25).read().decode("utf-8", "ignore")
    m = re.search(r"var ytInitialData = (\{.*?\});</script>", h)
    if not m:
        raise SystemExit("ERRO: não consegui ler a página do canal")
    out = []

    def walk(o):
        if isinstance(o, dict):
            if "lockupViewModel" in o:
                v = o["lockupViewModel"]
                s = json.dumps(v, ensure_ascii=False)
                t = re.search(r'"title": \{"content": "(.*?)"', s)
                tag = "ao vivo" if '"LIVE' in s or "_LIVE" in s else ("programado" if "UPCOMING" in s else "")
                if v.get("contentId") and t:
                    out.append({"id": v["contentId"], "titulo": t.group(1), "situacao": tag,
                                "link": "https://www.youtube.com/watch?v=" + v["contentId"]})
            for x in o.values():
                walk(x)
        elif isinstance(o, list):
            for x in o:
                walk(x)

    walk(json.loads(m.group(1)))
    return out


def achar(a, b):
    a, b = norm(a), norm(b)
    for v in videos():
        t = norm(v["titulo"])
        if a in t and b in t and "melhores momentos" not in t:
            return v
    return None


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("listar", "achar"):
        raise SystemExit(__doc__)
    if sys.argv[1] == "listar":
        for v in videos():
            print(f"{v['situacao'] or '-':10} {v['link']}  {v['titulo']}")
    else:
        v = achar(sys.argv[2], sys.argv[3])
        print(f"{v['link']}  {v['titulo']} ({v['situacao'] or 'gravado'})" if v else "nenhum vídeo do canal Paulistão para esse jogo")


if __name__ == "__main__":
    main()
