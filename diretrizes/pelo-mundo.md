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
2. Transfermarkt, Sofascore, Flashscore/Soccerway, FotMob: só para descobrir nomes. oGol: só números (veja a regra do Thiago).
3. Negócio só fechado. Empréstimo conta (o clube atual é o do empréstimo). Voltou ao Brasil: `voltou ID --obs "..."`
   (sai do radar e fica guardado).
4. Destaque (gol, título, transferência, marco, seleção): 2 fontes, texto curto e factual.
5. Jogos do dia: agenda publicada por veículo aceito (Lance!, ge, Diário do Nordeste, Correio etc.) ou site da liga.
   Horário de Brasília. Só as ligas do menu Internacional e as copas continentais. A marcação "Paulista em campo" é
   automática (jogadores do radar nos dois clubes).
6. Nada de apostas.

## Regra do Thiago (28/11/2026, vale para todas as divisões)
- **Monitoramento: 20 atletas por dia** que saíram de qualquer clube paulista (A1 a A4, Segunda Divisão, base) entre
  2023 e 2027 para o exterior. É o ponto de partida para atualizar clube atual e liga de cada um.
  `python3 ferramentas/pelo_mundo.py fila` mostra os do dia: primeiro os pendentes, depois os conferidos há mais tempo;
  completa os 20 com nomes novos (9 prioritários primeiro).
- **Só vai ao site quem tem figurinha E dados.** Dados = clube atual com 2 fontes (regra 1) + números da temporada e
  carreira (`numeros --json`, página do jogador no oGol, uma por vez, sem leitura em sequência). Figurinha = foto real
  de referência (enviada pelo Thiago ou anúncio oficial) passada no ChatGPT (`figurinha ID --img --ref`).
  O `gerar` deixa fora do site quem estiver incompleto e lista os nomes.
- oGol para números: liberado pelo Thiago (15/11 e 28/11). Continua proibido como fonte de clube, transferência ou título.

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

## Tarefa agendada (a criar: bloqueada pela checagem automática em 28/11, 3h30)
- "TSP · Paulistas pelo mundo: 20 atletas por dia", todo dia 19h41 (Brasília), precisa do Mac ligado (Chrome do
  Thiago com oGol e ChatGPT). Passos: `fila --n 20` (pendentes e conferidos há mais tempo) + nomes novos até 20
  (9 prioritários primeiro); clube atual com 2 fontes; números do oGol uma página por vez, navegando, 8 s entre
  páginas, parar se aparecer jogador errado ou bloqueio; figurinha só com foto real; `gerar`, `validar`, commit, push;
  resumo de até 6 linhas. Substitui as duas tarefas antigas (jogos do dia continuam num passo à parte, se o Thiago quiser).
