#!/usr/bin/env python3
"""Páginas pilares de pessoas (treinadores parceiros e outros) do TSP.

  python3 ferramentas/pessoas.py validar   → confere o dados/pessoas.json (respostas até 55 palavras, fontes, campos)
  python3 ferramentas/pessoas.py gerar     → valida e escreve api/pessoas.json (o tema TSP Nova Era 1.12.0+ lê a cada 30 min)
  python3 ferramentas/pessoas.py prompt "Nome"   → prompt da figurinha (ChatGPT) no padrão do Mercado da Bola
  python3 ferramentas/pessoas.py figurinha "Nome" --img ARQUIVO.png --ref URL   → grava a figurinha (webp 400x400) e liga à página

Cada pessoa vira a página /treinador/<nome>/ (endereço fixo, não muda quando o técnico troca de clube).
Quem também está no Mercado da Bola recebe por cima os campos daqui (pilar, exclusiva, ficha, carreira).
Regras: diretrizes/pessoas.md e diretrizes/paginas-pilares.md.
"""
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ARQ = RAIZ / "dados" / "pessoas.json"
SAIDA = RAIZ / "api" / "pessoas.json"
MAX = 55


def palavras(t):
    return len([w for w in str(t).split() if w.strip()])


def validar():
    d = json.loads(ARQ.read_text())
    erros = []
    nomes = set()
    for p in d.get("pessoas", []):
        n = p.get("nome", "")
        if not n:
            erros.append("pessoa sem nome")
            continue
        if n in nomes:
            erros.append(f"{n}: repetido")
        nomes.add(n)
        f = p.get("ficha") or {}
        if (f.get("titulos") or f.get("acessos")) and len(f.get("fontes") or []) < 2:
            erros.append(f"{n}: título/acesso exige 2 fontes em ficha.fontes")
        pil = p.get("pilar") or {}
        if pil:
            if palavras(pil.get("resposta_rapida", "")) > MAX:
                erros.append(f"{n}: resposta_rapida com {palavras(pil['resposta_rapida'])} palavras (máx. {MAX})")
            for s in pil.get("secoes", []):
                if not s.get("h2", "").endswith("?"):
                    erros.append(f"{n}: H2 '{s.get('h2')}' deve ser pergunta")
                w = palavras(s.get("resposta", ""))
                if not w or w > MAX:
                    erros.append(f"{n}: resposta de '{s.get('h2')}' com {w} palavras (máx. {MAX})")
            if len(pil.get("titulo", "")) > 75:
                erros.append(f"{n}: título SEO longo ({len(pil['titulo'])} caracteres)")
            if len(pil.get("descricao", "")) > 160:
                erros.append(f"{n}: descrição com {len(pil['descricao'])} caracteres (máx. 160)")
        for c in p.get("carreira", []):
            if not c.get("temporada") or not c.get("clube"):
                erros.append(f"{n}: linha de carreira sem temporada ou clube")
    return d, erros


CORES = RAIZ / "dados" / "cores_clubes.json"
PROMPT = ("Gere uma imagem: retrato para FIGURINHA DE ÁLBUM DE FUTEBOL, formato quadrado 1:1, estilo foto de estúdio "
          "levemente ilustrada, do TREINADOR da imagem anexada, com rosto, cabelo e barba fiéis à referência. Ele veste {roupa}. "
          "SEM patrocinadores, SEM marcas, SEM número e SEM nenhum texto. Do peito para cima, de frente, expressão confiante, "
          "fundo liso em degradê {fundo}, sem moldura.")


def pessoa(d, nome):
    p = next((x for x in d["pessoas"] if x["nome"].lower() == nome.lower()), None)
    if not p:
        raise SystemExit(f"{nome}: não está em dados/pessoas.json")
    return p


def cmd_prompt(nome):
    d = json.loads(ARQ.read_text())
    p = pessoa(d, nome)
    cl = p.get("clube") or ""
    cores = (json.loads(CORES.read_text()) if CORES.exists() else {}).get(cl, "")
    if cl:
        roupa = f"a camisa polo de comissão técnica do clube (cores: {cores or 'oficiais do clube'}), com o escudo do clube no peito, do lado esquerdo, como na segunda imagem anexada"
        fundo = f"das cores do clube ({cores or 'oficiais'})"
    else:
        roupa = "uma camisa polo lisa azul-marinho, sem escudo (ele está sem clube)"
        fundo = "cinza-grafite com detalhe laranja"
    print(PROMPT.format(roupa=roupa, fundo=fundo))
    print("Referência: foto oficial do treinador (de preferência enviada por ele ou publicada pelo clube). Sem referência, não gere.")


def cmd_figurinha(nome, img, ref):
    from PIL import Image
    if not ref.startswith("https://"):
        raise SystemExit("ERRO: --ref = link https da foto oficial usada como referência")
    d = json.loads(ARQ.read_text())
    p = pessoa(d, nome)
    slug = "pessoa-" + "".join(c if c.isalnum() else "-" for c in __import__("unicodedata").normalize("NFKD", nome).encode("ascii", "ignore").decode().lower()).strip("-")
    destino = RAIZ / "api" / "figurinhas" / f"{slug}.webp"
    destino.parent.mkdir(parents=True, exist_ok=True)
    im = Image.open(img).convert("RGB")
    lado = min(im.size)
    im = im.crop(((im.width - lado) // 2, 0, (im.width + lado) // 2, lado)).resize((400, 400), Image.LANCZOS)
    im.save(destino, "WEBP", quality=82)
    import datetime
    p["foto"] = {"url": f"https://raw.githubusercontent.com/tudosobrepaulistas/tsp-dados/main/api/figurinhas/{slug}.webp",
                 "credito": "Montagem com IA (ilustrativa) · TSP", "fonte": ref, "ia": True,
                 "em": datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3))).isoformat(timespec="seconds")}
    ARQ.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n")
    print("gravado", destino.relative_to(RAIZ))


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "validar"
    if cmd == "prompt":
        return cmd_prompt(sys.argv[2])
    if cmd == "figurinha":
        a = sys.argv[2:]
        return cmd_figurinha(a[0], a[a.index("--img") + 1], a[a.index("--ref") + 1])
    d, erros = validar()
    for e in erros:
        print("ERRO:", e)
    if erros:
        sys.exit(1)
    print(f"ok: {len(d.get('pessoas', []))} pessoas")
    if cmd == "gerar":
        SAIDA.write_text(json.dumps({"pessoas": d["pessoas"]}, ensure_ascii=False, indent=1) + "\n")
        print("escrito", SAIDA.relative_to(RAIZ))


if __name__ == "__main__":
    main()
