#!/usr/bin/env python3
"""Páginas pilares de pessoas (treinadores parceiros e outros) do TSP.

  python3 ferramentas/pessoas.py validar   → confere o dados/pessoas.json (respostas até 55 palavras, fontes, campos)
  python3 ferramentas/pessoas.py gerar     → valida e escreve api/pessoas.json (o tema TSP Nova Era 1.12.0+ lê a cada 30 min)

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


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "validar"
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
