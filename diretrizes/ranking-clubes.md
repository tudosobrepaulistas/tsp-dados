# Página do clube em 1º na busca "notícias do <clube>" (meta do Thiago, 24/11/2026)

**Meta:** todo clube do interior no **top 3** do Google para "notícias do <clube>" (o ideal é o 1º); os 4 grandes
(Corinthians, Palmeiras, Santos, São Paulo) no **top 5**. A página que disputa é a do clube: `/times/<slug>/`.
Ferramenta: `python3 ferramentas/ranking.py` (fila, pagina, registrar, relatorio). Histórico: `dados/seo/ranking_clubes.json`.

## Quem ganha hoje essa busca (amostra de 24/11/2026)
Páginas-hub de clube com lista de notícias frescas: Gazeta Esportiva (/times/xv-de-piracicaba/), Lance! e Band
(/tudo-sobre/<clube>/), CNN e Exame (/noticias-sobre/<clube>/), o site oficial do clube e páginas de estatística
(Sofascore, FotMob, Flashscore). Ou seja: vence quem tem **a página do clube mais fresca, mais completa e mais citada**.

## Cada execução (até 6 clubes, gastando pouco)
1. `python3 ferramentas/ranking.py fila --n 6`. Para cada clube da lista:
2. **Busca (1 WebSearch, modo standard)** com a frase exata que a fila mostra. Anote a posição do
   tudosobrepaulista.com.br (qualquer endereço do TSP conta, mas diga qual apareceu) e os 5 primeiros domínios.
   Não apareceu = `posicao: null`. Esse buscador NÃO é o Google: é um sinal. Quando houver número do Search Console
   (consulta "notícias do <clube>", posição média dos últimos 7 dias), registre também com `"motor": "search_console"`.
3. **Raio-X da página:** `python3 ferramentas/ranking.py pagina SLUG` (frescor e ficha).
4. **Ações, nesta ordem (só o que estiver faltando):**
   a. **Frescor (o que mais pesa):** sem matéria do clube nas últimas 24h → escreva **1 matéria** do clube (notícia das
      últimas 48h confirmada em 2 fontes ou nota oficial com link), seguindo `diretrizes/maquina.md` e passando no
      `python3 ferramentas/maquina.py adicionar`. No máximo **2 matérias por execução**, primeiro o clube mais longe da meta.
      Sem notícia nova confirmada, não escreva: anote "sem pauta" (nada de evergreen aqui).
   b. **Ficha do clube** (o que a página mostra na Resposta rápida e no FAQ): preencha até 4 campos que faltam
      (fundação, estádio e capacidade, cores, títulos com anos, site e Instagram oficiais, presidente), cada um com
      fonte (site oficial, FPF, matéria aceita). Grave em /tmp/guia.json `{"<slug>": {...campos, "fontes": [...]}}` e rode
      `python3 ferramentas/guia.py juntar /tmp/guia.json && python3 ferramentas/guia.py gerar`.
   c. **Título e descrição:** só se o clube ficou fora da meta duas vezes seguidas e o vencedor usa uma forma que o TSP não
      usa (apelido, cidade, "hoje"). Item em `api/titulos.json` com `"url": "/times/<slug>/"`, título até 60 caracteres
      começando por "Notícias do <clube>", descrição até 155 com a cidade e a divisão de 2027 (regras em
      `diretrizes/editor-seo.md`). Nada de caça-clique.
5. `python3 ferramentas/ranking.py registrar --json /tmp/ranking.json` com uma linha por clube (posição, top 5, ações
   feitas, obs como "sem pauta" ou "ficha completa").
6. `python3 ferramentas/ranking.py relatorio | head -1`, commit em português ("ranking clubes: N conferidos, M matérias,
   K fichas") e push no main (conflito: git pull --rebase). Matéria nova: `python3 ferramentas/maquina.py avisar-site`.
7. Resumo de até 5 linhas: placar da meta, clubes que subiram ou caíram, ações feitas e o que depende do Thiago.

## Regras
- Nunca invente dado de ficha; nunca copie Sofascore, Flashscore, FotMob, Transfermarkt ou oGol (só referência).
- Nada de apostas. Nada de comprar link, trocar link em massa, texto escondido ou página só para robô.
- Não crie página nova por clube: a página que disputa é sempre `/times/<slug>/` (uma palavra-chave por URL).

## O que depende do Thiago (fora do alcance da tarefa)
- Search Console: dar acesso à conta que está no navegador do Claude, para medir a posição real no Google toda semana.
- Links de fora: parcerias com rádios, jornais e o próprio clube do interior citando a página do clube no TSP.
- Google Notícias (Publisher Center) com o TSP cadastrado.
