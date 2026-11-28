# Radar TSP "Paulistas pelo mundo" (28/11/2026, layout aprovado pelo Thiago)

Quem saiu de um clube paulista (base ou time profissional) e joga fora do Brasil, do Real Madrid à 2ª divisão da Coreia.

## Onde aparece (tema TSP Nova Era 1.14.0, inc/pelo-mundo.php)
- `/paulistas-pelo-mundo/`: o Radar (números, filtros por clube de origem, país, divisão, base/profissional e busca;
  destaques da semana; todos por país; "Avise a redação").
- `/paulistas-pelo-mundo/<id>/`: ficha (resposta rápida, posição, clube atual, país e divisão, títulos lá fora,
  trajetória, próximo jogo, notícias dele no TSP, também saíram do mesmo clube, fontes).
- Home: faixa "Paulistas pelo mundo" depois da tabela da Série A (3 últimas matérias internacionais ou, sem elas,
  os jogadores do radar) com "Jogos de hoje no mundo".
- `/campeonato/futebol-internacional/`: "Jogos de hoje" (abas Hoje e Amanhã, por liga) e os paulistas lá fora.
- Matéria internacional cujo título cita um jogador do radar: selo "Paulista pelo mundo · ex-<clube>" e chapéu
  "Ex-<clube> · <clube atual>" nos cards. Basta escrever o nome do jogador no título como está no radar.
- Liga de "Outras ligas" com jogador do radar abre sozinha no menu Internacional (ex.: Russo, por causa do Jhon Jhon).
- Mapa do site: `/tsp-mapa-pelo-mundo.xml` (entra no índice do Yoast).

## Base
- `dados/pelo_mundo.json` (jogadores e destaques) e `dados/jogos_mundo.json` (jogos do dia). Nunca à mão:
  `python3 ferramentas/pelo_mundo.py` (veja `--help`). Depois: `gerar`, `validar`, commit e push.
- Jogador: nome, posição, nascimento, origem (clube paulista do site, base ou profissional, ano de saída), clube atual
  (clube, país, liga, divisão, desde), trajetória (cada etapa com fonte), títulos lá fora (com fonte), foto real com
  crédito (opcional), fontes.

## Regras (as de sempre, CLAUDE.md)
1. Clube atual com 2 fontes aceitas (imprensa brasileira, grandes jornais do país do clube, site/rede oficial do clube
   ou da liga). Clube pequeno do exterior: 1 anúncio oficial + 1 matéria.
2. oGol, Transfermarkt, Sofascore, Flashscore/Soccerway, FotMob: só para descobrir nomes. Nunca são fonte nem são copiados.
3. Negócio só fechado. Empréstimo conta (o clube atual é o do empréstimo). Voltou ao Brasil: `voltou ID --obs "..."`
   (sai do radar e fica guardado).
4. Destaque (gol, título, transferência, marco, seleção): 2 fontes, texto curto e factual.
5. Jogos do dia: agenda publicada por veículo aceito (Lance!, ge, Diário do Nordeste, Correio etc.) ou site da liga.
   Horário de Brasília. Só as ligas do menu Internacional e as copas continentais. A marcação "Paulista em campo" é
   automática (jogadores do radar nos dois clubes).
6. Nada de apostas.

## Rotina (tarefas agendadas)
- Todo dia de manhã: jogos de hoje e de amanhã no mundo (`jogos --data`), saídas do Mercado da Bola para o exterior,
  destaques do dia anterior (gols e títulos dos jogadores do radar, 2 fontes).
- Toda semana: conferir o clube atual de cada jogador (quem trocou, quem voltou) e descobrir novos nomes, começando pelos
  9 clubes prioritários (Guarani, Ponte Preta, XV de Piracicaba, Portuguesa, Bragantino, Novorizontino, Mirassol,
  Botafogo-SP, Comercial) e depois os 4 grandes e o resto do interior.

## Primeira carga (28/11/2026)
7 jogadores, 6 países: Estêvão (Chelsea), Endrick (Real Madrid), Luis Guilherme (Sporting), Jhon Jhon (Zenit),
Sorriso (Famalicão), Weverton (Kyoto Sanga, ex-Ponte Preta) e Gabriel Martinelli (Al-Hilal, ex-Ituano).
Descartados por falta de 2 fontes atuais: João Victor (Daejeon, ex-Guarani; só há fonte do empréstimo de 2025) e
Kewen (a ida ao Penafiel não se concretizou).

## Tarefas agendadas (a criar: a criação foi bloqueada pela checagem automática em 28/11)
- "TSP · Paulistas pelo mundo: jogos do dia e destaques", todo dia 7h37 (Brasília): passos 2 a 4 da "Rotina" acima.
- "TSP · Paulistas pelo mundo: conferência e descoberta", domingo 15h43: conferir clube atual de quem tem
  "conferido" com mais de 7 dias e descobrir 10 jogadores novos por semana (9 prioritários primeiro).
