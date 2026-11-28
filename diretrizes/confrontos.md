# Página de confronto: a mais completa da internet (25/11/2026, regra do Thiago)

Todo jogo futuro de competição que tem clube paulista (Série A, Série B, Copa do Brasil, Libertadores, Sul-Americana,
Paulistão, Copinha...) ganha a página /confronto/time-a-x-time-b/ **completa pelo menos 3 dias antes do jogo**, mesmo
quando nenhum dos dois é paulista. Concorrentes a bater: oGol, FootyStats, ge, Sofascore. Eles são só **referência de formato**:
nunca copiar dado deles (regras 3 e 4 do CLAUDE.md). Nada de odds, apostas ou palpite.

## Intenções de busca que a página TEM que responder (todas)
| Intenção | De onde vem | Quando |
|---|---|---|
| Quando é / que dia / que horas | base (jogo-novo/remarcar) | sempre |
| Onde vai ser (estádio e cidade) | base | sempre |
| Onde assistir / transmissão | prejogo.onde_assistir (comunicado ou matéria) | até 72h antes |
| Quem apita / VAR | prejogo.arbitragem (escala da CBF/FPF ou matéria) | quando a escala sair |
| Ingressos (preço, venda) | prejogo.ingressos (site do clube ou matéria) | quando anunciado |
| O que está em jogo | prejogo.analise + tabela (automático) | até 72h antes |
| Como estão na tabela | automático (classificação da base) | sempre |
| Como chegam (últimos 5, mandante em casa, visitante fora) | automático | sempre |
| Estatísticas comparadas (gols, média, sem sofrer gol, os dois marcam, 3+ gols, cartões) | automático | sempre |
| Artilheiros de cada time | automático (artilharia da base) | sempre |
| Técnicos e números deles, técnico x técnico | automático (tecnicos.json) + prováveis | sempre |
| Prováveis escalações, desfalques, dúvidas | prejogo.provaveis | 6h a 4h antes (e já 72h antes se houver matéria) |
| Retrospecto geral (jogos, vitórias de cada um, empates, gols) | **prejogo.confronto.total** (2 fontes de sites diferentes) | até 72h antes |
| Recortes (no Brasileirão, no estádio do mandante, mata-matas) | prejogo.confronto.recortes (com fonte) | se houver matéria |
| Primeiro jogo, último encontro, maiores vitórias, jogos marcantes, decisões | prejogo.confronto (com fonte) | até 72h antes |
| Artilheiros do confronto, curiosidades | prejogo.confronto (com fonte) | se houver matéria |
| Todos os jogos entre os dois na base | automático | sempre |
| Notícias dos dois | automático | sempre |

Dado sem fonte = fica de fora ou aparece "Em atualização". Nunca estimar.

## Como gravar o dossiê histórico
`python3 ferramentas/tsp.py prejogo ID --json /tmp/pre.json` com:
```json
{"confronto": {
  "times": ["Coritiba", "Flamengo"],
  "total": {"jogos": 70, "vitorias": [18, 35], "empates": 17, "gols": [80, 120], "ate": "novembro de 2026"},
  "recortes": [{"nome": "No Couto Pereira", "jogos": 30, "vitorias": [12, 9], "empates": 9}],
  "primeiro": "Flamengo 3 x 1 Coritiba, 02/05/1965, Torneio Roberto Gomes Pedrosa, no Maracanã",
  "ultimo": "Flamengo 2 x 0 Coritiba, 12/07/2026, Brasileirão",
  "maiores": ["Maior vitória do Coritiba: ...", "Maior vitória do Flamengo: ..."],
  "marcantes": ["..."], "decisoes": ["..."], "artilheiros": ["..."], "curiosidades": ["..."],
  "fontes": ["https://ge.globo.com/...", "https://www.lance.com.br/..."]}}
```
- `total` só com 2 fontes de sites diferentes que tragam o MESMO número (a ferramenta confere que jogos = vitórias + empates + vitórias).
  Fontes que discordam: use o número do site oficial de um dos clubes ou da matéria mais recente que cite o levantamento
  e diga quem fez o levantamento em `curiosidades`; se não houver acordo, grave só os jogos marcantes.
- Fontes aceitas: as do CLAUDE.md (ge, Lance!, UOL, ESPN notícias, sites oficiais, jornais regionais...). Proibido: oGol,
  Sofascore, FootyStats, Transfermarkt, Flashscore e afins, mesmo como "segunda fonte".
- Também grave `retrospecto` (1 parágrafo), `analise`, `onde_assistir`, `arbitragem` ({"arbitro", "var", "fontes"}) e
  `ingressos` ({"texto", "fontes"}) — ver diretrizes/prejogo.md.

## Rotina diária (tarefa agendada "Confrontos 72h")
1. `python3 ferramentas/tsp.py agenda --horas 96` → jogos dos próximos 4 dias.
2. Para cada jogo de competição acompanhada (prioridade: paulistas, depois Série A, depois Série B): se o prejogo não tem
   `confronto`, `analise` e `onde_assistir`, pesquisa (WebSearch "retrospecto X x Y", site oficial, ge) e grava.
3. Na véspera: arbitragem (escala da CBF) e ingressos. No dia: prováveis escalações (diretrizes/prejogo.md).
4. `calcular`, `validar`, commit "confronto: X x Y (dossiê)", push.

## Onde assistir: link só da Federação Paulista (28/11/2026, regra do Thiago)
Jogo transmitido pela FPF (canal Paulistão no YouTube): coloque o link do vídeo do jogo no lide e na linha "Onde assistir".
Ache o link no canal Paulistão do YouTube (ao vivo/programados) ou na página do jogo no site da FPF; confira o título pelo
oEmbed (https://www.youtube.com/oembed?url=<link>&format=json) antes de publicar. Os outros canais vão só pelo nome, sem link.

