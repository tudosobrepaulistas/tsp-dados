#!/usr/bin/env python3
"""Loja do clube (/produtos/<clube>/): vitrine com filtros + conteúdo SEO/GEO/AEO + schema.

  python3 afiliados/gerar_loja.py palmeiras   -> afiliados/artigos/loja-palmeiras.html

Catálogo: afiliados/shopee-links.json (itens com "clube") e, quando existir, afiliados/catalogo-<clube>.json
(mesmo formato: produto, preco_13_11, vendas, link, imagem, loja). Conteúdo do clube: afiliados/lojas.json.
"""
import html
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
SITE = "https://tudosobrepaulista.com.br"

CATS = [("Camisas e roupas", r"camisa|camiseta|body|vestido|blusa|moletom"),
        ("Chinelos e meias", r"chinelo|havaianas|meia|meião"),
        ("Canecas e copos", r"caneca|copo|taça|kit caipirinha|dose"),
        ("Garrafas e squeezes", r"garrafa|squeeze"),
        ("Casa e banho", r"toalha|lençol|manta|cobertor|almofada|balde"),
        ("Bola e treino", r"bola|luva|goleiro"),
        ("Churrasco", r"faca|churras"),
        ("Acessórios", r"chaveiro|pin|broche|pulseira|bracelete|necessaire|estojo|bolsa|boné|rel[óo]gio|mochila|lancheira|caneta"),
        ("Kits de presente", r"kit")]
MARCAS = ["Havaianas", "Puma", "Betel", "Rikam", "Buettner", "Jolitex", "Supercap", "Sport Bel", "Sestini", "BrasFoot",
          "Torcida Baby", "Döhler", "Sportcom", "Avanti"]
FAIXAS = [("ate30", "Até R$ 30", 0, 30), ("30a60", "R$ 30 a 60", 30, 60), ("60a100", "R$ 60 a 100", 60, 100), ("100mais", "Acima de R$ 100", 100, 10**6)]


def e(t):
    return html.escape(str(t), quote=True)


def num(p):
    return float(re.sub(r"[^\d,]", "", p).replace(",", ".") or 0)


def vend(v):
    m = re.search(r"\d+", v or "")
    return int(m.group()) if m else 0


def categoria(n):
    n2 = n.lower()
    if re.search(r"\bkit\b", n2) and not re.search(r"lençol|meia|caneta|caipirinha|copo dose|2 copo", n2):
        return "Kits de presente"
    for c, rx in CATS:
        if re.search(rx, n2):
            return c
    return "Acessórios"


def marca(n):
    for m in MARCAS:
        if m.lower() in n.lower():
            return m
    return "Outras licenciadas"


def publico(n):
    return "Infantil" if re.search(r"infantil|beb[êe]|baby|kids|juvenil|criança|recem", n, re.I) else "Adulto"


def card(it):
    p = num(it["preco_13_11"])
    v = vend(it["vendas"])
    faixa = next(k for k, _, a, b in FAIXAS if a <= p < b)
    loja = it.get("loja", "Shopee")
    bd = f'<span class="bd">{v} vendas no mês</span>' if v >= 20 else ""
    return (f'<li class="tspl-card" data-cat="{e(it["cat"])}" data-marca="{e(it["marca"])}" data-pub="{e(it["pub"])}" '
            f'data-loja="{e(loja)}" data-faixa="{faixa}" data-preco="{p:.2f}" data-vendas="{v}">'
            f'<a class="im" href="{e(it["link"])}" target="_blank" rel="sponsored nofollow noopener">'
            f'<img src="{e(it["imagem"])}" alt="{e(it["produto"])}" loading="lazy" width="300" height="300"></a>'
            f'<div class="tx"><span class="ct">{e(it["cat"])}</span><h3 class="nm">{e(it["produto"])}</h3>{bd}'
            f'<div class="pr">{e(it["preco_13_11"])}</div><div class="mt">na {e(loja)} · oficial e licenciado · preço de {e(it.get("data", "13/11/2026"))}</div>'
            f'<a class="bt" href="{e(it["link"])}" target="_blank" rel="sponsored nofollow noopener">Ver na {e(loja)}</a></div></li>')


CSS = """<style>
.tspl{color:#1b1b1b}.tspl *{box-sizing:border-box}
.tspl-hero{background:var(--cor);color:#fff;border-radius:16px;padding:20px;margin:0 0 14px}
.tspl-hero p{margin:0;color:#fff;opacity:.95}
.tspl-aviso{font-size:12.5px;color:#555;background:#f6f6f4;border-radius:10px;padding:10px 12px;margin:0 0 16px}
.tspl-resp{border-left:4px solid var(--cor);background:#fafaf7;padding:12px 14px;margin:0 0 18px;border-radius:0 10px 10px 0}
.tspl-resp p{margin:0}
.tspl-f{position:sticky;top:0;z-index:5;background:#fff;border:1px solid #e6e6e6;border-radius:12px;padding:10px;margin:0 0 12px}
.tspl-chips{display:flex;gap:6px;overflow-x:auto;padding-bottom:6px;scrollbar-width:thin}
.tspl-chips button{flex:none;border:1px solid #d9d9d9;background:#fff;border-radius:999px;padding:6px 12px;font-size:13px;font-weight:700;cursor:pointer;color:#222}
.tspl-chips button[aria-pressed=true]{background:var(--cor);border-color:var(--cor);color:#fff}
.tspl-sel{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:6px;margin-top:6px}
@media(min-width:700px){.tspl-sel{grid-template-columns:repeat(5,minmax(0,1fr))}}
.tspl-sel select,.tspl-sel label{font-size:13px;border:1px solid #d9d9d9;border-radius:8px;padding:7px;background:#fff;width:100%;color:#222}
.tspl-sel label{display:flex;align-items:center;gap:6px}
.tspl-n{font-size:13px;color:#555;margin:4px 0 10px}
.tspl-grid{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
@media(min-width:700px){.tspl-grid{grid-template-columns:repeat(4,minmax(0,1fr))}}
.tspl-card{border:1px solid #e5e5e5;border-radius:12px;background:#fff;display:flex;flex-direction:column;overflow:hidden;margin:0}
.tspl-card[hidden]{display:none}
.tspl-card .im{aspect-ratio:1/1;background:#fafafa;display:block}
.tspl-card .im img{width:100%;height:100%;object-fit:contain;margin:0}
.tspl-card .tx{padding:9px;display:flex;flex-direction:column;gap:5px;flex:1}
.tspl-card .ct{font-size:10.5px;text-transform:uppercase;letter-spacing:.03em;color:#777;font-weight:700}
.tspl-card .nm{font-size:13px;font-weight:700;line-height:1.3;margin:0;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden;min-height:50px}
.tspl-card .pr{font-size:18px;font-weight:800;color:#0a7a3d}
.tspl-card .mt{font-size:10.5px;color:#777}
.tspl-card .bd{font-size:11px;font-weight:700;color:#8a4b00;background:#fff3d6;border-radius:6px;padding:2px 6px;align-self:flex-start}
.tspl-card .bt{margin-top:auto;display:block;text-align:center;background:#ee4d2d;color:#fff;border-radius:8px;padding:9px 6px;font-weight:800;font-size:13px;text-decoration:none}
.tspl-guia{display:block;border:2px solid var(--cor);border-radius:12px;padding:12px 14px;margin:18px 0;text-decoration:none;color:#111}
.tspl-top{list-style:none;margin:0 0 18px;padding:0;display:flex;flex-direction:column;gap:8px;counter-reset:none}
.tspl-top li{margin:0}
.tspl-top a{display:flex;align-items:center;gap:10px;border:1px solid #e5e5e5;border-radius:12px;padding:8px;text-decoration:none;color:#111;background:#fff}
.tspl-top .rk{flex:none;width:34px;text-align:center;font-weight:900;font-size:18px;color:var(--cor)}
.tspl-top li{display:flex;align-items:center;gap:6px}
.tspl-top li a{flex:1;min-width:0}
.tspl-top img{width:64px;height:64px;object-fit:contain;flex:none;margin:0;border-radius:8px;background:#fafafa}
.tspl-top .tt{display:flex;flex-direction:column;min-width:0;font-size:13px}
.tspl-top .tt strong{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.tspl-top .tt em{font-style:normal;color:#0a7a3d;font-weight:700;font-size:12px}
.tspl-top .go{margin-left:auto;flex:none;background:#ee4d2d;color:#fff;border-radius:8px;padding:7px 10px;font-weight:800;font-size:12px}
.tspl h2.tspl-top-t{font-size:20px;margin:18px 0 10px}
.tspl h2{margin:26px 0 8px}.tspl h3.q{font-size:16px;margin:14px 0 4px}
.tspl table{width:100%;border-collapse:collapse;font-size:14px}.tspl td,.tspl th{border:1px solid #e3e3e3;padding:7px;text-align:left}
</style>"""

JS = """<script>
(function(){var r=document.querySelector('.tspl');if(!r)return;var g=r.querySelector('.tspl-grid'),cs=[].slice.call(g.children),n=r.querySelector('.tspl-n b'),st={cat:''};
function q(s){return r.querySelector(s)}
function ap(){var f=q('#tf-faixa').value,m=q('#tf-marca').value,p=q('#tf-pub').value,l=q('#tf-loja').value,o=q('#tf-ord').value,k=0;
cs.forEach(function(c){var ok=(!st.cat||c.dataset.cat===st.cat)&&(!f||c.dataset.faixa===f)&&(!m||c.dataset.marca===m)&&(!p||c.dataset.pub===p)&&(!l||c.dataset.loja===l);c.hidden=!ok;if(ok)k++;});
var s=cs.slice().sort(function(a,b){return o==='menor'?a.dataset.preco-b.dataset.preco:o==='maior'?b.dataset.preco-a.dataset.preco:b.dataset.vendas-a.dataset.vendas});s.forEach(function(c){g.appendChild(c)});n.textContent=k;}
[].forEach.call(r.querySelectorAll('.tspl-chips button'),function(b){b.addEventListener('click',function(){st.cat=b.dataset.v;[].forEach.call(r.querySelectorAll('.tspl-chips button'),function(x){x.setAttribute('aria-pressed',x===b)});ap();});});
[].forEach.call(r.querySelectorAll('.tspl-sel select'),function(s){s.addEventListener('change',ap)});
var h=decodeURIComponent((location.hash||'').slice(1));if(h){var b=[].filter.call(r.querySelectorAll('.tspl-chips button'),function(x){return x.dataset.slug===h})[0];if(b)b.click();}
})();
</script>"""


def slug(t):
    t = t.lower()
    for a, b in (("áàâã", "a"), ("éê", "e"), ("í", "i"), ("óôõ", "o"), ("ú", "u"), ("ç", "c")):
        for ch in a:
            t = t.replace(ch, b)
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def main(clube):
    conf = json.loads((RAIZ / "lojas.json").read_text(encoding="utf-8"))[clube]
    itens = [i for i in json.loads((RAIZ / "shopee-links.json").read_text(encoding="utf-8"))["itens"] if i.get("clube") == clube]
    extra = RAIZ / f"catalogo-{clube}.json"
    if extra.exists():
        vistos = {i["link"] for i in itens}
        itens += [i for i in json.loads(extra.read_text(encoding="utf-8"))["itens"] if i["link"] not in vistos]
    minimo = conf.get("min_vendas", 30)
    unicos = {}
    for it in itens:
        if vend(it["vendas"]) >= minimo and it["produto"] not in unicos:
            unicos[it["produto"]] = it
    itens = list(unicos.values())
    for it in itens:
        it["cat"], it["marca"], it["pub"] = categoria(it["produto"]), marca(it["produto"]), publico(it["produto"])
    itens.sort(key=lambda x: -vend(x["vendas"]))
    cats = [c for c, _ in CATS if any(i["cat"] == c for i in itens)]
    marcas = sorted({i["marca"] for i in itens})
    lojas = sorted({i.get("loja", "Shopee") for i in itens})
    nome = conf["nome"]
    precos = [num(i["preco_13_11"]) for i in itens]
    url = f"{SITE}/produtos/{clube}/"

    p = [CSS, f'<div class="tspl" style="--cor:{conf["cor"]}">',
         f'<div class="tspl-hero"><p>{conf["hero"]}</p></div>',
         f'<p class="tspl-aviso"><strong>Importante: o Tudo Sobre Paulista não é a loja oficial do {e(nome)} e não vende nenhum produto.</strong> '
         'Somos um site de notícias que seleciona e recomenda itens; os botões levam para lojas parceiras (links de afiliado). Se você comprar, '
         'recebemos uma pequena comissão, sem custo a mais para você. A compra, a entrega e a troca são feitas pela loja vendedora. '
         f'Só listamos anúncios que se apresentam como oficiais ou licenciados e com pelo menos {minimo} vendas no mês. '
         'Preços vistos na data indicada: confira o valor atualizado na loja.</p>',
         f'<h2 class="tspl-top-t">Top 5 do mês: os achadinhos do {e(nome)} que mais vendem</h2>',
         '<ol class="tspl-top">' + "".join(
             f'<li><span class="rk">{k + 1}º</span><a href="{e(i["link"])}" target="_blank" rel="sponsored nofollow noopener">'
             f'<img src="{e(i["imagem"])}" alt="{e(i["produto"])}" width="72" height="72" loading="lazy">'
             f'<span class="tt"><strong>{e(i["produto"])}</strong><em>{vend(i["vendas"])} vendas no mês · {e(i["preco_13_11"])}</em></span>'
             f'<span class="go">Ver</span></a></li>' for k, i in enumerate(itens[:5])) + '</ol>',
         f'<div class="tspl-resp"><p><strong>Resposta rápida:</strong> {conf["resposta"]}</p></div>',
         f'<h2 class="tspl-top-t">Todos os achadinhos do {e(nome)}</h2>',
         '<div class="tspl-f" role="region" aria-label="Filtros da loja">',
         '<div class="tspl-chips"><button type="button" data-v="" data-slug="" aria-pressed="true">Tudo</button>'
         + "".join(f'<button type="button" data-v="{e(c)}" data-slug="{slug(c)}" aria-pressed="false">{e(c)}</button>' for c in cats) + '</div>',
         '<div class="tspl-sel">'
         '<select id="tf-ord" aria-label="Ordenar"><option value="vendidos">Mais vendidos</option><option value="menor">Menor preço</option><option value="maior">Maior preço</option></select>'
         '<select id="tf-faixa" aria-label="Faixa de preço"><option value="">Qualquer preço</option>' + "".join(f'<option value="{k}">{t}</option>' for k, t, _, _ in FAIXAS) + '</select>'
         '<select id="tf-marca" aria-label="Marca"><option value="">Todas as marcas</option>' + "".join(f'<option>{e(m)}</option>' for m in marcas) + '</select>'
         '<select id="tf-pub" aria-label="Para quem"><option value="">Adulto e infantil</option><option>Adulto</option><option>Infantil</option></select>'
         '<select id="tf-loja" aria-label="Loja"><option value="">Todas as lojas</option>' + "".join(f'<option>{e(l)}</option>' for l in lojas) + '</select>'
         '</div></div>',
         f'<p class="tspl-n"><b>{len(itens)}</b> produtos oficiais do {e(nome)} · só oficiais e licenciados</p>',
         '<ul class="tspl-grid">' + "".join(card(i) for i in itens) + '</ul>',
         f'<a class="tspl-guia" href="{SITE}/materia/{conf["guia"]}/"><strong>Não sabe o que escolher?</strong> Veja o guia {e(conf["guia_titulo"])} →</a>']
    for h2, txt in conf["secoes"]:
        p.append(f'<h2>{e(h2)}</h2><p>{txt}</p>')
    p.append('<h2>Faixas de preço dos produtos oficiais</h2><table><thead><tr><th>Tipo de produto</th><th>Do mais barato ao mais caro</th><th>Itens</th></tr></thead><tbody>')
    for c in cats:
        pc = sorted(num(i["preco_13_11"]) for i in itens if i["cat"] == c)
        fx = f'R$ {pc[0]:.2f}'.replace('.', ',') + (f' a R$ {pc[-1]:.2f}'.replace('.', ',') if len(pc) > 1 else '')
        p.append(f'<tr><td>{e(c)}</td><td>{fx}</td><td>{len(pc)}</td></tr>')
    p.append('</tbody></table>')
    p.append('<h2>Perguntas frequentes</h2>')
    for q_, a_ in conf["faq"]:
        p.append(f'<h3 class="q">{e(q_)}</h3><p>{e(a_)}</p>')
    p.append('</div>')
    ld = [{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": "Início", "item": SITE + "/"},
              {"@type": "ListItem", "position": 2, "name": "Produtos do Torcedor", "item": SITE + "/produtos/"},
              {"@type": "ListItem", "position": 3, "name": f"Loja do {nome}", "item": url}]},
          {"@context": "https://schema.org", "@type": "CollectionPage", "name": conf["titulo"], "url": url,
           "about": {"@type": "SportsTeam", "name": conf["time_nome"]},
           "mainEntity": {"@type": "ItemList", "numberOfItems": len(itens), "itemListElement": [
               {"@type": "ListItem", "position": k + 1, "name": i["produto"]} for k, i in enumerate(itens[:30])]}},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
              {"@type": "Question", "name": q_, "acceptedAnswer": {"@type": "Answer", "text": a_}} for q_, a_ in conf["faq"]]}]
    p.append('<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + '</script>')
    p.append(JS)
    out = RAIZ / "artigos" / f"loja-{clube}.html"
    out.write_text("\n".join(p), encoding="utf-8")
    print("ok", out.name, len(itens), "itens", f"R$ {min(precos):.2f}–{max(precos):.2f}", cats)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "palmeiras")
