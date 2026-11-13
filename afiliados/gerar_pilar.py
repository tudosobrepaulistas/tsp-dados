#!/usr/bin/env python3
"""Página pilar "Produtos do Torcedor" (vitrine + guias). Grava afiliados/artigos/pilar-produtos.html.

Dados: afiliados/shopee-links.json (produto, preço, vendas, link, imagem, clube) e afiliados/guias.json (guias).
"""
import html
import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
DATA = "13/11/2026"
ESC = "https://tudosobrepaulista.com.br/wp-content/uploads/tsp-escudos/"
CLUBES = [("palmeiras", "Palmeiras", "escudo-94-1720474166.png", "presente-para-palmeirense", "#0a6b38"),
          ("corinthians", "Corinthians", "escudo-93-1720474165.png", "presente-para-corinthiano", "#111111"),
          ("sao-paulo", "São Paulo", "escudo-96-1720474167.png", "presente-para-sao-paulino", "#bf1520"),
          ("santos", "Santos", "escudo-95-1720474166.png", "presente-para-santista", "#333333")]

CSS = """<style>
.tspp{--v:#ee4d2d;font-family:inherit;color:#1b1b1b}
.tspp *{box-sizing:border-box}
.tspp-hero{background:#0f3d24;color:#fff;border-radius:16px;padding:22px 20px;margin:0 0 18px}
.tspp-hero h2{color:#fff;margin:0 0 8px;font-size:26px;line-height:1.2}
.tspp-hero p{margin:0 0 12px;color:#e6f2ea}
.tspp-chips{display:flex;flex-wrap:wrap;gap:8px;margin:0}
.tspp-chips a{display:inline-flex;align-items:center;gap:6px;background:#fff;color:#111;border-radius:999px;padding:6px 12px;text-decoration:none;font-weight:700;font-size:14px}
.tspp-chips img{width:20px;height:20px}
.tspp-aviso{font-size:13px;color:#555;background:#f6f6f4;border-radius:10px;padding:10px 12px;margin:0 0 22px}
.tspp h2.tspp-t{font-size:22px;margin:28px 0 4px;display:flex;align-items:center;gap:8px}
.tspp h2.tspp-t img{width:28px;height:28px}
.tspp .tspp-sub{margin:0 0 12px;color:#555;font-size:14px}
.tspp-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}
@media(min-width:700px){.tspp-grid{grid-template-columns:repeat(4,minmax(0,1fr))}}
.tspp-card{border:1px solid #e5e5e5;border-radius:12px;background:#fff;display:flex;flex-direction:column;overflow:hidden}
.tspp-card .im{aspect-ratio:1/1;background:#fafafa;display:flex;align-items:center;justify-content:center}
.tspp-card .im img{width:100%;height:100%;object-fit:contain;margin:0}
.tspp-card .tx{padding:10px;display:flex;flex-direction:column;gap:6px;flex:1}
.tspp-card .nm{font-size:13px;font-weight:700;line-height:1.3;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden;min-height:50px}
.tspp-card .pr{font-size:18px;font-weight:800;color:#0a7a3d}
.tspp-card .mt{font-size:11px;color:#777}
.tspp-card .bd{font-size:11px;font-weight:700;color:#8a4b00;background:#fff3d6;border-radius:6px;padding:2px 6px;align-self:flex-start}
.tspp-card a.bt{margin-top:auto;display:block;text-align:center;background:var(--v);color:#fff;border-radius:8px;padding:9px 6px;font-weight:800;font-size:13px;text-decoration:none}
.tspp-guia{display:flex;gap:12px;align-items:center;border:2px solid #0a7a3d;border-radius:12px;padding:12px 14px;margin:0 0 12px;text-decoration:none;color:#111;background:#f3fbf6}
.tspp-guia strong{display:block;font-size:16px}
.tspp-guia span{font-size:13px;color:#444}
.tspp-guia img{width:40px;height:40px;flex:none}
.tspp-faq h3{font-size:16px;margin:14px 0 4px}
.tspp-faq p{margin:0;color:#333}
</style>"""


def e(t):
    return html.escape(str(t), quote=True)


def vendas(v):
    n = re.search(r"\d+", v or "")
    return int(n.group()) if n else 0


def card(it):
    nome = it.get("titulo_curto") or it["produto"]
    bd = f'<span class="bd">{vendas(it["vendas"])} vendas no mês</span>' if vendas(it["vendas"]) >= 20 else ""
    return (f'<div class="tspp-card"><a class="im" href="{e(it["link"])}" target="_blank" rel="sponsored nofollow noopener">'
            f'<img src="{e(it["imagem"])}" alt="{e(it["produto"])}" loading="lazy" width="300" height="300"></a>'
            f'<div class="tx"><div class="nm" title="{e(it["produto"])}">{e(it["produto"])}</div>{bd}'
            f'<div class="pr">{e(it["preco_13_11"])}</div><div class="mt">preço visto em {DATA} · oficial e licenciado</div>'
            f'<a class="bt" href="{e(it["link"])}" target="_blank" rel="sponsored nofollow noopener">Ver na Shopee</a></div></div>')


def main():
    itens = json.loads((RAIZ / "shopee-links.json").read_text(encoding="utf-8"))["itens"]
    guias = {g["slug"]: g for g in json.loads((RAIZ / "guias.json").read_text(encoding="utf-8"))}
    p = [CSS, '<div class="tspp">',
         '<div class="tspp-hero"><h2>Achadinhos do torcedor paulista</h2>'
         '<p>Presentes e produtos <strong>oficiais e licenciados</strong> de Palmeiras, Corinthians, São Paulo e Santos, '
         'escolhidos pelo que mais vende e pelo uso no dia a dia. Black Friday em 27/11 e Natal logo depois: confira e compre com antecedência.</p>'
         '<div class="tspp-chips">'
         + "".join(f'<a href="#{s}"><img src="{ESC}{img}" alt="Escudo do {n}" width="20" height="20">{n}</a>' for s, n, img, _, _ in CLUBES)
         + '</div></div>',
         '<p class="tspp-aviso"><strong>Transparência:</strong> esta página tem links de afiliado da Shopee. Se você comprar por eles, '
         'o Tudo Sobre Paulista recebe uma pequena comissão, sem custo a mais para você. Só listamos produtos anunciados como oficiais '
         f'e licenciados, com vendas no mês. Preços vistos em {DATA}: podem mudar, confira na loja.</p>',
         '<h2 class="tspp-t">Mais vendidos da semana</h2><p class="tspp-sub">Os produtos oficiais dos clubes paulistas que mais saem na Shopee.</p>',
         '<div class="tspp-grid">' + "".join(card(i) for i in sorted(itens, key=lambda x: -vendas(x["vendas"]))[:8]) + '</div>']
    for s, n, img, guia, cor in CLUBES:
        g = guias[guia]
        p.append(f'<h2 class="tspp-t" id="{s}"><img src="{ESC}{img}" alt="Escudo do {n}" width="28" height="28">{n}</h2>')
        p.append(f'<a class="tspp-guia" href="https://tudosobrepaulista.com.br/materia/{guia}/"><img src="{ESC}{img}" alt="" width="40" height="40">'
                 f'<div><strong>Guia: {e(g["titulo"])}</strong><span>Para quem é cada presente, que problema resolve e o que observar antes de comprar →</span></div></a>')
        lista = sorted([i for i in itens if i["clube"] == s], key=lambda x: -vendas(x["vendas"]))
        p.append('<div class="tspp-grid">' + "".join(card(i) for i in lista) + '</div>')
    p.append('<div class="tspp-faq"><h2 class="tspp-t">Perguntas frequentes</h2>'
             '<h3>Os produtos desta página são oficiais?</h3><p>Todos são anunciados na Shopee como oficiais e licenciados pelos clubes. Antes de comprar, confira o selo, a loja e as avaliações na página do produto.</p>'
             '<h3>O Tudo Sobre Paulista vende esses produtos?</h3><p>Não. Indicamos e explicamos; a compra, a entrega e a troca são feitas pela Shopee e pela loja vendedora.</p>'
             '<h3>Os preços estão atualizados?</h3><p>Os preços são os vistos em ' + DATA + '. Eles mudam com frequência, principalmente na Black Friday: o valor certo é o que aparece na Shopee.</p>'
             '<h3>Qual o presente mais vendido para torcedor?</h3><p>Nos clubes paulistas, chinelos Havaianas oficiais, garrafas e canecas licenciadas estão entre os itens que mais vendem.</p></div>')
    p.append('</div>')
    (RAIZ / "artigos" / "pilar-produtos.html").write_text("\n".join(p), encoding="utf-8")
    print("ok", len("\n".join(p)))


if __name__ == "__main__":
    main()
