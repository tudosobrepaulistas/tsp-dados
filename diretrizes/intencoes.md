# Intenções de busca antes de cada jogo (regra do Thiago, 12/11/2026)

O Google mostra o que o torcedor procura antes do jogo ("onde assistir Mirassol x Atlético-MG", "provável escalação",
"raio-x", "últimos jogos", "estatísticas", "partidas de"). É busca útil, mas caduca no apito inicial. Por isso,
**todo jogo de clube paulista** (qualquer série/competição que esteja na base) ganha **3 matérias de serviço**
no intervalo entre o jogo anterior e o jogo, uma por intenção, sempre nos horários das pontas do dia
(**6h, 12h e 23h59**) para não disputar espaço com o noticiário:

| Intenção | Quando sai | Título (palavra-chave no começo, sem repetir a das outras) | O que tem |
|---|---|---|---|
| `raio-x` | 1º horário da janela (até 72h antes) | "Raio-X de Mirassol x Atlético-MG: últimos jogos, retrospecto e estatísticas" | últimos 5 jogos de cada (da base do TSP), retrospecto do confronto, campanha, artilheiros, mandante/visitante |
| `escalacoes` | véspera / manhã do jogo | "Provável escalação de Mirassol x Atlético-MG: desfalques e dúvidas" | provável time de cada lado, suspensos, lesionados, dúvidas, técnico |
| `onde-assistir` | último horário antes do jogo | "Onde assistir Mirassol x Atlético-MG: horário e transmissão" | canal/streaming confirmado, horário de Brasília, estádio, arbitragem (se divulgada) |

O `maquina.py intencoes` já calcula o horário de cada uma (e soma 3 minutos quando dois jogos caem no mesmo horário).

## Regras
1. **Nada inventado.** Escalação provável: só o que 2 fontes jornalísticas ou o clube publicaram (treino, coletiva).
   Onde assistir: só transmissão anunciada oficialmente (clube, federação, emissora) ou em 2 fontes. Não confirmou? Pule
   a matéria (não escreva "a confirmar"). Números do raio-x: base do TSP (`api/tsp.json`, já conferida) e fontes aceitas.
2. **Palpite fica de fora**: o TSP não faz conteúdo de aposta.
3. **Sem canibalização**: cada matéria tem a sua palavra-chave (`foco`): "raio-x X x Y", "provável escalação X x Y",
   "onde assistir X x Y". Não repita o título de outra. Cite no texto o link da página do jogo
   (`https://tudosobrepaulista.com.br/jogo/...`) e, se já existir, das outras matérias do mesmo jogo.
4. Primeiro parágrafo responde direto à pergunta (AEO): "Mirassol x Atlético-MG será transmitido pelo Premiere,
   neste sábado (14/11), às 18h30, no Maião."
5. Foto real com crédito, de jogo recente do clube paulista (olhe antes, `foto.mostra` honesto).
6. JSON como em `diretrizes/maquina.md`, com `"tipo": "noticia"`, `"clube"`: o clube paulista do jogo,
   `"publish_at"`: o horário que `intencoes` mostrou, e `"intencao": {"jogo": ID, "tipo": "raio-x"}` (ou escalacoes / onde-assistir).
   Essas matérias ficam fora da cota diária.
