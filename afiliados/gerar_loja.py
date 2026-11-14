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


LOJAS_TODAS = ["Mercado Livre", "Shopee"]
VENDAS = [("50", "Mais de 50 no mês", 50), ("20", "Mais de 20 no mês", 20)]


def card(it):
    p = num(it["preco_13_11"])
    v = vend(it["vendas"])
    faixa = next(k for k, _, a, b in FAIXAS if a <= p < b)
    loja = it.get("loja", "Shopee")
    cls = "ml" if loja == "Mercado Livre" else "sh"
    rk = f'<span class="rk">{it["rank"]}º mais vendido</span>' if it.get("rank") else ""
    return (f'<li class="tspl-card" data-cat="{e(it["cat"])}" data-marca="{e(it["marca"])}" data-pub="{e(it["pub"])}" '
            f'data-loja="{e(loja)}" data-faixa="{faixa}" data-preco="{p:.2f}" data-vendas="{v}">'
            f'<a class="im" href="{e(it["link"])}" target="_blank" rel="sponsored nofollow noopener">{rk}'
            f'<img src="{e(it["imagem"])}" alt="{e(it["produto"])}" loading="lazy" width="300" height="300"></a>'
            f'<div class="tx"><h3 class="nm">{e(it["produto"])}</h3>'
            f'<div class="pr">{e(it["preco_13_11"])}</div><div class="vd">{v} vendidos no mês</div>'
            f'<div class="mt"><span class="lj {cls}">{e(loja)}</span> oficial e licenciado</div>'
            f'<a class="bt {cls}" href="{e(it["link"])}" target="_blank" rel="sponsored nofollow noopener">Ver na {e(loja)}</a></div></li>')


CSS = """<style>
.tspl{color:#1b1b1b;--sh:#ee4d2d;--ml:#ffe600}.tspl *{box-sizing:border-box}
.tspl-sub{margin:0 0 10px;color:#444;font-size:15px}
.tspl-av{display:flex;gap:8px;align-items:flex-start;font-size:12.5px;color:#5b4a00;background:#fff8d9;border:1px solid #f1e3a3;border-radius:10px;padding:8px 12px;margin:0 0 14px}
.tspl-av a{color:inherit}
.tspl-chips{display:flex;gap:6px;overflow-x:auto;padding:0 0 8px;margin:0 0 6px;scrollbar-width:thin}
.tspl-chips button{flex:none;border:1px solid #d9d9d9;background:#fff;border-radius:999px;padding:6px 12px;font-size:13px;font-weight:700;cursor:pointer;color:#222}
.tspl-chips button[aria-pressed=true]{background:var(--cor);border-color:var(--cor);color:#fff}
.tspl-bar{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin:0 0 10px}
.tspl-sr{position:absolute!important;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
.tspl-bar{flex-wrap:nowrap}.tspl-bar .n{font-size:13px;color:#555;margin-right:auto}
.tspl-bar select{font-size:13px;border:1px solid #d9d9d9;border-radius:8px;padding:7px;background:#fff;color:#222}
.tspl-fbtn{border:1px solid var(--cor);color:var(--cor);background:#fff;border-radius:8px;padding:7px 12px;font-weight:800;font-size:13px;cursor:pointer}
.tspl-ativos{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 10px}
.tspl-ativos:empty{display:none}
.tspl-ativos button{border:0;background:#eef3ef;border-radius:999px;padding:5px 10px;font-size:12px;font-weight:700;cursor:pointer;color:#222}
.tspl-ativos .lp{background:none;color:var(--cor);text-decoration:underline}
.tspl-lay{display:block}
.tspl-side{display:none;border:1px solid #e6e6e6;border-radius:12px;padding:12px;margin:0 0 12px;background:#fff}
.tspl-side.on{display:block}
.tspl-side fieldset{border:0;border-bottom:1px solid #eee;margin:0 0 10px;padding:0 0 10px}
.tspl-side fieldset:last-child{border-bottom:0;margin:0;padding:0}
.tspl-side legend{font-weight:800;font-size:14px;margin:0 0 6px;padding:0}
.tspl-side label{display:flex;align-items:center;gap:7px;font-size:13px;padding:3px 0;cursor:pointer;color:#222}
.tspl-side label.off{color:#aaa;cursor:default}
.tspl-side label i{font-style:normal;color:#888;margin-left:auto;font-size:12px}
.tspl-side input[type=checkbox],.tspl-side input[type=radio]{accent-color:var(--cor);margin:0}
.tspl-faixa{display:flex;gap:6px;margin-top:6px}
.tspl-faixa input{width:100%;min-width:0;font-size:13px;border:1px solid #d9d9d9;border-radius:8px;padding:6px}
.tspl-faixa button{border:0;background:var(--cor);color:#fff;border-radius:8px;padding:0 10px;font-weight:800;cursor:pointer}
@media(min-width:760px){.tspl-lay{display:grid;grid-template-columns:200px minmax(0,1fr);gap:16px;align-items:start}
.tspl-side{display:block;position:sticky;top:12px;max-height:calc(100vh - 24px);overflow:auto;margin:0}.tspl-fbtn{display:none}}
.tspl-grid{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
@media(min-width:960px){.tspl-grid{grid-template-columns:repeat(3,minmax(0,1fr))}}
.tspl-card{border:1px solid #e5e5e5;border-radius:12px;background:#fff;display:flex;flex-direction:column;overflow:hidden;margin:0;transition:box-shadow .15s}
.tspl-card:hover{box-shadow:0 4px 14px rgba(0,0,0,.08)}
.tspl-card[hidden]{display:none}
.tspl-card .im{position:relative;aspect-ratio:1/1;background:#fafafa;display:block}
.tspl-card .im img{width:100%;height:100%;object-fit:contain;margin:0}
.tspl-card .rk{position:absolute;top:6px;left:6px;background:var(--cor);color:#fff;font-size:10.5px;font-weight:800;border-radius:6px;padding:3px 6px}
.tspl-card .tx{padding:9px;display:flex;flex-direction:column;gap:4px;flex:1}
.tspl-card .nm{font-size:13px;font-weight:600;line-height:1.3;margin:0;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;min-height:34px}
.tspl-card .pr{font-size:19px;font-weight:800;color:#111}
.tspl-card .vd{font-size:11.5px;color:#0a7a3d;font-weight:700}
.tspl-card .mt{font-size:10.5px;color:#777;display:flex;align-items:center;gap:5px}
.tspl-card .lj{font-weight:800;border-radius:4px;padding:1px 5px;font-size:10px}
.tspl-card .lj.sh{background:#fde8e3;color:#c43a1d}.tspl-card .lj.ml{background:#fff6b3;color:#333}
.tspl-card .bt{margin-top:auto;display:block;text-align:center;border-radius:8px;padding:9px 6px;font-weight:800;font-size:13px;text-decoration:none}
.tspl-card .bt.sh{background:var(--sh);color:#fff}.tspl-card .bt.ml{background:var(--ml);color:#2d3277}
.tspl-vazio{display:none;text-align:center;padding:24px;color:#555}
.tspl-info{margin-top:30px;border-top:3px solid var(--cor);padding-top:6px}
.tspl-resp{border-left:4px solid var(--cor);background:#fafaf7;padding:12px 14px;margin:12px 0 18px;border-radius:0 10px 10px 0}
.tspl-resp p{margin:0}
.tspl-guia{display:block;border:2px solid var(--cor);border-radius:12px;padding:12px 14px;margin:18px 0;text-decoration:none;color:#111}
.tspl-info ol{padding-left:22px}.tspl-info ol li{margin:0 0 4px}
.tspl h2{margin:26px 0 8px}.tspl h3.q{font-size:16px;margin:14px 0 4px}
.tspl table{width:100%;border-collapse:collapse;font-size:14px}.tspl td,.tspl th{border:1px solid #e3e3e3;padding:7px;text-align:left}
.tspl-aviso{font-size:12.5px;color:#555;background:#f6f6f4;border-radius:10px;padding:10px 12px;margin:18px 0 0}
</style>"""

JS = """<script>
(function(){var r=document.querySelector('.tspl');if(!r)return;var g=r.querySelector('.tspl-grid'),cs=[].slice.call(g.children),st={cat:'',loja:[],marca:[],pub:'',faixa:'',min:0,max:0,vend:0};
function q(s){return r.querySelector(s)}function qa(s){return [].slice.call(r.querySelectorAll(s))}
function ok(c,sem){var d=c.dataset,p=+d.preco;return (sem==='cat'||!st.cat||d.cat===st.cat)&&(sem==='loja'||!st.loja.length||st.loja.indexOf(d.loja)>=0)&&(sem==='marca'||!st.marca.length||st.marca.indexOf(d.marca)>=0)&&(sem==='pub'||!st.pub||d.pub===st.pub)&&(sem==='faixa'||((!st.faixa||d.faixa===st.faixa)&&(!st.min||p>=st.min)&&(!st.max||p<=st.max)))&&(sem==='vend'||!st.vend||+d.vendas>=st.vend)}
function conta(){qa('.tspl-side input[data-f]').forEach(function(i){var f=i.dataset.f,v=i.value,k=0;if(v==='')return;cs.forEach(function(c){if(!ok(c,f))return;var d=c.dataset;if(f==='vend'?+d.vendas>=+v:f==='faixa'?d.faixa===v:d[f]===v)k++;});var l=i.closest('label'),b=l.querySelector('i');if(b)b.textContent='('+k+')';var off=k===0&&!i.checked;i.disabled=off;l.classList.toggle('off',off);});}
function chips(){var a=q('.tspl-ativos'),h='',t=[];if(st.cat)t.push(['cat',st.cat]);st.loja.forEach(function(v){t.push(['loja',v])});st.marca.forEach(function(v){t.push(['marca',v])});if(st.pub)t.push(['pub',st.pub]);if(st.faixa)t.push(['faixa',q('.tspl-side input[data-f=faixa][value="'+st.faixa+'"]').dataset.t]);if(st.min||st.max)t.push(['mm','R$ '+(st.min||0)+' a '+(st.max||'…')]);if(st.vend)t.push(['vend','+'+st.vend+' vendas']);
t.forEach(function(x){h+='<button type="button" data-k="'+x[0]+'" data-v="'+x[1]+'">'+x[1]+' ✕</button>'});if(t.length)h+='<button type="button" class="lp" data-k="tudo">Limpar filtros</button>';a.innerHTML=h;}
function ap(){var o=q('#tf-ord').value,k=0;cs.forEach(function(c){var v=ok(c);c.hidden=!v;if(v)k++;});
cs.slice().sort(function(a,b){return o==='menor'?a.dataset.preco-b.dataset.preco:o==='maior'?b.dataset.preco-a.dataset.preco:b.dataset.vendas-a.dataset.vendas}).forEach(function(c){g.appendChild(c)});
q('.tspl-bar .n b').textContent=k;q('.tspl-vazio').style.display=k?'none':'block';conta();chips();}
function setCat(v){st.cat=v;qa('.tspl-chips button').forEach(function(x){x.setAttribute('aria-pressed',x.dataset.v===v)});}
qa('.tspl-chips button').forEach(function(b){b.addEventListener('click',function(){setCat(b.dataset.v);ap();});});
qa('.tspl-side input[data-f]').forEach(function(i){i.addEventListener('change',function(){var f=i.dataset.f;if(f==='loja'||f==='marca'){st[f]=qa('.tspl-side input[data-f='+f+']:checked').map(function(x){return x.value});}else if(f==='vend'){st.vend=i.checked?+i.value:0;qa('.tspl-side input[data-f=vend]').forEach(function(x){if(x!==i)x.checked=false});}else{st[f]=i.value;}ap();});});
q('.tspl-faixa button').addEventListener('click',function(){st.min=+q('#tf-min').value||0;st.max=+q('#tf-max').value||0;ap();});
q('#tf-ord').addEventListener('change',ap);
q('.tspl-fbtn').addEventListener('click',function(){var s=q('.tspl-side');s.classList.toggle('on');this.setAttribute('aria-expanded',s.classList.contains('on'));});
q('.tspl-ativos').addEventListener('click',function(ev){var b=ev.target.closest('button');if(!b)return;var k=b.dataset.k,v=b.dataset.v;
if(k==='tudo'||k==='cat')setCat('');if(k==='tudo'){st.loja=[];st.marca=[];st.pub='';st.faixa='';st.min=st.max=st.vend=0;qa('.tspl-side input').forEach(function(i){if(i.type==='number')i.value='';else i.checked=i.value===''&&i.type==='radio';});}
if(k==='loja'||k==='marca'){st[k]=st[k].filter(function(x){return x!==v});qa('.tspl-side input[data-f='+k+']').forEach(function(i){if(i.value===v)i.checked=false});}
if(k==='pub'||k==='faixa'){st[k]='';var z=q('.tspl-side input[data-f='+k+'][value=""]');if(z)z.checked=true;}
if(k==='mm'){st.min=st.max=0;q('#tf-min').value='';q('#tf-max').value='';}if(k==='vend'){st.vend=0;qa('.tspl-side input[data-f=vend]').forEach(function(i){i.checked=false});}ap();});
var h=decodeURIComponent((location.hash||'').slice(1));if(h){var b=qa('.tspl-chips button').filter(function(x){return x.dataset.slug===h})[0];if(b)setCat(b.dataset.v);}ap();
})();
</script>"""


def facet(f, opcoes, tipo="checkbox", todos=None):
    out = []
    if todos:
        out.append(f'<label><input type="radio" name="tf-{f}" data-f="{f}" value="" checked> {e(todos)}</label>')
    for v, t in opcoes:
        extra = f' data-t="{e(t)}"' if f == "faixa" else ""
        out.append(f'<label><input type="{tipo}" name="tf-{f}" data-f="{f}" value="{e(v)}"{extra}> {e(t)} <i></i></label>')
    return "".join(out)


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

    for k, it in enumerate(itens[:5]):
        it["rank"] = k + 1
    apel = conf.get("apelido", nome)
    p = [CSS, f'<div class="tspl" style="--cor:{conf["cor"]}">',
         f'<p class="tspl-sub">{len(itens)} produtos <strong>oficiais e licenciados do {e(nome)}</strong> escolhidos pelo que mais vende. '
         f'Filtre por loja, preço e marca e compre direto na loja parceira.</p>',
         f'<p class="tspl-av"><span aria-hidden="true">ℹ️</span><span><strong>Não somos a loja oficial do {e(nome)}.</strong> '
         'O Tudo Sobre Paulista é um site de notícias que recomenda produtos com links de afiliado: a compra é feita na loja parceira. '
         '<a href="#tspl-transparencia">Entenda</a></span></p>',
         '<div class="tspl-chips" role="group" aria-label="Tipo de produto"><button type="button" data-v="" data-slug="" aria-pressed="true">Tudo</button>'
         + "".join(f'<button type="button" data-v="{e(c)}" data-slug="{slug(c)}" aria-pressed="false">{e(c)}</button>' for c in cats) + '</div>',
         '<div class="tspl-bar"><span class="n"><b>' + str(len(itens)) + '</b> resultados</span>'
         '<button type="button" class="tspl-fbtn" aria-expanded="false">☰ Filtros</button>'
         '<label><span class="tspl-sr">Ordenar por</span><select id="tf-ord" aria-label="Ordenar por">'
         '<option value="vendidos">Mais vendidos</option><option value="menor">Menor preço</option><option value="maior">Maior preço</option></select></label></div>',
         '<div class="tspl-ativos" aria-live="polite"></div>',
         '<div class="tspl-lay"><aside class="tspl-side" aria-label="Filtros">',
         '<fieldset><legend>Loja</legend>' + facet("loja", [(l, l) for l in LOJAS_TODAS]) + '</fieldset>',
         '<fieldset><legend>Preço</legend>' + facet("faixa", [(k, t) for k, t, _, _ in FAIXAS], "radio", "Qualquer preço")
         + '<div class="tspl-faixa"><input id="tf-min" type="number" min="0" placeholder="Mín." aria-label="Preço mínimo">'
           '<input id="tf-max" type="number" min="0" placeholder="Máx." aria-label="Preço máximo"><button type="button" aria-label="Aplicar faixa de preço">›</button></div></fieldset>',
         '<fieldset><legend>Mais vendidos</legend>' + facet("vend", [(v, t) for v, t, _ in VENDAS]) + '</fieldset>',
         '<fieldset><legend>Para quem</legend>' + facet("pub", [("Adulto", "Adulto"), ("Infantil", "Infantil")], "radio", "Todos") + '</fieldset>',
         '<fieldset><legend>Marca</legend>' + facet("marca", [(m, m) for m in marcas]) + '</fieldset>',
         '</aside><div>',
         '<ul class="tspl-grid">' + "".join(card(i) for i in itens) + '</ul>',
         '<p class="tspl-vazio">Nenhum produto com esses filtros. <strong>Tente limpar algum filtro.</strong></p>',
         '</div></div>',
         f'<section class="tspl-info"><h2>{e(conf["titulo"])}</h2><p>{conf["hero"]}</p>',
         f'<div class="tspl-resp"><p><strong>Resposta rápida:</strong> {conf["resposta"]}</p></div>',
         f'<h2>Top 5 do mês: os achadinhos do {e(nome)} que mais vendem</h2><ol>'
         + "".join(f'<li><a href="{e(i["link"])}" target="_blank" rel="sponsored nofollow noopener">{e(i["produto"])}</a> — '
                   f'{vend(i["vendas"])} vendas no mês, {e(i["preco_13_11"])} na {e(i.get("loja", "Shopee"))}</li>' for i in itens[:5]) + '</ol>',
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
    p.append(f'<p class="tspl-aviso" id="tspl-transparencia"><strong>Transparência: o Tudo Sobre Paulista não é a loja oficial do {e(nome)} e não vende nenhum produto.</strong> '
             'Somos um site de notícias que seleciona e recomenda itens; os botões levam para lojas parceiras (links de afiliado). Se você comprar, '
             'recebemos uma pequena comissão, sem custo a mais para você. A compra, a entrega e a troca são feitas pela loja vendedora. '
             f'Só listamos anúncios que se apresentam como oficiais ou licenciados e com pelo menos {minimo} vendas no mês. '
             'Preços vistos na data indicada: confira o valor atualizado na loja.</p></section>')
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
