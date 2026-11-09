# Temporada completa dos times das Séries A e B (banco de dados do TSP)

Pedido do Thiago (09/11/2026): ter **todos os jogos oficiais da temporada** de cada time das Séries A e B (estadual,
Copa do Nordeste, Copa Verde, Copa do Brasil, Libertadores, Sul-Americana, Brasileirão), **todos os jogadores que
entraram em campo** e o **elenco com foto e dados**, para as páginas /time/ e /jogador/ e as estatísticas do TSP
(aproveitamento com e sem cada jogador, minutos, gols com ele em campo, previsões). O modelo de organização é parecido
com o do oGol, mas **nenhum dado é copiado de banco de estatística** (oGol/zerozero, Sofascore, Flashscore, Transfermarkt,
FotMob, FootyStats, BeSoccer, Wikipedia de estatística sem fonte). Tudo sai de matéria jornalística aceita e site oficial.

## Cada execução (um time por vez, até ~20 jogos)
1. `python3 ferramentas/tsp.py temporada` mostra a fila (o time com menos jogos registrados primeiro). Pegue o primeiro
   que ainda não está completo e rode `python3 ferramentas/tsp.py temporada CHAVE` para ver o que já existe.
2. Descubra a lista de jogos oficiais do time em 2026: página de jogos/resultados do **site oficial do clube**, tabelas da
   CBF e das federações estaduais, e matérias de cada rodada. Competição que ainda não existe na base:
   `python3 ferramentas/tsp.py competicao-nova --chave baiano --nome "Campeonato Baiano"` (formato "historico").
   Chaves sugeridas: paulistao_a1, carioca, mineiro, gaucho, paranaense, catarinense, baiano, pernambucano, cearense,
   goiano, paraense, alagoano, sergipano, potiguar, paraibano, maranhense, piauiense, matogrossense, sulmatogrossense,
   capixaba, brasiliense, amazonense, nordestao, copa_verde, sul_americana (já existe), copa_do_brasil (já existe).
3. Para cada jogo que falta, com **2 fontes** que digam o mesmo placar e, de preferência, a **ficha técnica**:
   ```
   python3 ferramentas/tsp.py jogo-passado --comp baiano --data "2026-01-18 16:00" --casa "Vitória" --fora "Bahia" --placar 1x1 \
     --fontes URL1 URL2 [--fase "Final - ida"] [--rodada 3] [--estadio X] [--cidade Y] [--penaltis 4x3] \
     [--gols "casa|Fulano|23|normal; fora|Beltrano|45+2|penalti"] [--esc /tmp/esc.json]
   ```
   Escalação no formato de `diretrizes/banco-times.md`, agora também com cartões quando a ficha trouxer:
   `"cartoes": {"amarelos": [{"jogador": "Fulano", "minuto": "33"}], "vermelhos": [{"jogador": "Beltrano", "minuto": "80"}]}`
   (dentro de "casa"/"fora"). Nomes de jogadores sempre iguais entre gols, escalação e elenco (como o clube escreve).
   Jogo de Série A/B que já existe na base sem escalação: `python3 ferramentas/tsp.py escalacao ID --json ...`.
4. Elenco com foto e dados (site oficial do clube, página de cada jogador quando houver):
   `{"nome", "nome_completo", "apelidos": [], "posicao", "numero", "nascimento": "AAAA-MM-DD", "nacionalidade", "altura": "1,85 m",
   "pe": "Direito", "foto": {"url": "https://...", "credito": "Foto: Fulano/Clube", "fonte": "https://página-do-jogador"}}`
   → `python3 ferramentas/tsp.py elenco CHAVE --json /tmp/elenco.json`. Só o que o site oficial mostra; sem foto oficial, sem foto.
5. `python3 ferramentas/tsp.py calcular && python3 ferramentas/tsp.py validar`, commit ("temporada: <time> +N jogos") e push.
   Placar sem 2 fontes ou ficha confusa: pule o jogo e anote no resumo. Nunca invente nem estime gols, minutos ou nomes.
