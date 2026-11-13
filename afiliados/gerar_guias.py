#!/usr/bin/env python3
"""Gera os guias de presente (HTML para o editor do WordPress) a partir dos dados abaixo.

  python3 afiliados/gerar_guias.py   -> grava afiliados/artigos/<slug>.html e afiliados/artigos/<slug>.json (SEO)
"""
import html
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
SAIDA = RAIZ / "artigos"
DATA = "13/11/2026"

AVISO = ("<strong>Transparência:</strong> este guia tem links de afiliado da Shopee. Se você comprar por eles, "
         "o Tudo Sobre Paulista recebe uma pequena comissão, sem custo a mais para você. "
         "Só indicamos produtos anunciados como <strong>oficiais e licenciados</strong> pelo clube e com vendas "
         "constantes. Preços vistos em " + DATA + ": podem mudar, confira na loja antes de comprar.")


def esc(t):
    return html.escape(t, quote=False)


def bloco_produto(p):
    link = p["link"]
    out = [f'<h3>{esc(p["nome"])}</h3>',
           f'<p><strong>Para quem é:</strong> {esc(p["quem"])}</p>',
           f'<p><strong>Que problema resolve:</strong> {esc(p["dor"])}</p>',
           f'<p><strong>Por que entrou na lista:</strong> {esc(p["porque"])}</p>']
    if p.get("atencao"):
        out.append(f'<p><strong>Fique de olho:</strong> {esc(p["atencao"])}</p>')
    out.append(f'<p><strong>Preço em {DATA}:</strong> cerca de {esc(p["preco"])}.</p>')
    out.append(f'<p><a href="{link}" target="_blank" rel="sponsored nofollow noopener">'
               f'Ver preço atual e avaliações na Shopee</a></p>')
    return "\n".join(out)


def cta(g):
    """Caixa de chamada no meio da matéria: o campeão de vendas + motivo real para decidir agora (sem escassez inventada)."""
    p = g["produtos"][g.get("cta", 0)]
    return ('<div style="border:2px solid #0a7a3d;border-radius:12px;padding:16px 18px;margin:24px 0;background:#f3fbf6">'
            f'<p style="margin:0 0 6px"><strong>O mais pedido da lista: {esc(p["curto"])}</strong></p>'
            f'<p style="margin:0 0 10px">{esc(p["dor"][0].upper() + p["dor"][1:])} É o presente que o torcedor usa no dia seguinte, '
            'e não um enfeite que fica na gaveta. Black Friday em 27/11 e Natal logo depois: compre com antecedência '
            'para chegar a tempo.</p>'
            f'<p style="margin:0"><a href="{p["link"]}" target="_blank" rel="sponsored nofollow noopener" '
            'style="display:inline-block;background:#0a7a3d;color:#fff;padding:10px 18px;border-radius:8px;'
            f'text-decoration:none;font-weight:bold">Ver preço de hoje na Shopee</a></p></div>')


def gerar(g):
    partes = [f'<p><em>{AVISO}</em></p>', f'<p>{g["abertura"]}</p>',
              '<h2>Resposta rápida: qual presente escolher?</h2>',
              '<table><thead><tr><th>Se o torcedor…</th><th>Presente</th><th>Faixa de preço</th></tr></thead><tbody>']
    for perfil, idx in g["rapida"]:
        p = g["produtos"][idx]
        partes.append(f'<tr><td>{esc(perfil)}</td><td><a href="{p["link"]}" target="_blank" '
                      f'rel="sponsored nofollow noopener">{esc(p["curto"])}</a></td><td>{esc(p["preco"])}</td></tr>')
    partes.append('</tbody></table>')
    partes.append(f'<h2>{esc(g["h2_lista"])}</h2>')
    for i, p in enumerate(g["produtos"]):
        partes.append(bloco_produto(p))
        if i == 2:
            partes.append(cta(g))
    partes.append(f'<h2>{esc(g["h2_oficial"])}</h2>')
    partes.append(f'<p>{g["oficial"]}</p>')
    partes.append('<h2>Como escolhemos os presentes desta lista?</h2>')
    partes.append(f'<p>{g["como"]}</p>')
    partes.append('<h2>Dicas para acertar no presente</h2><ul>' + "".join(f"<li>{esc(d)}</li>" for d in g["dicas"]) + '</ul>')
    # FAQ não vai no corpo: o tema mostra a seção "Perguntas frequentes" + schema a partir de api/materias.json
    partes.append(f'<p>{g["fecho"]}</p>')
    return "\n\n".join(partes)


def main():
    SAIDA.mkdir(exist_ok=True)
    for g in json.loads((RAIZ / "guias.json").read_text(encoding="utf-8")):
        (SAIDA / f'{g["slug"]}.html').write_text(gerar(g), encoding="utf-8")
        seo = {k: g[k] for k in ("titulo", "slug", "meta_title", "meta_desc", "foco", "tags", "faq")}
        (SAIDA / f'{g["slug"]}.json').write_text(json.dumps(seo, ensure_ascii=False, indent=1), encoding="utf-8")
        print("ok", g["slug"], len(gerar(g)))


if __name__ == "__main__":
    main()
