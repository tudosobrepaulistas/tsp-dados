# Planejador diário (roda às 2h)

1. Repositório: chame add_repo (owner "tudosobrepaulistas", repo "tsp-dados", access "push"), clone e leia CLAUDE.md.
2. **Calendário dos próximos 7 dias.** Para cada competição com status "ativa" em dados/competicoes.json, confira se todos os
   jogos dos próximos 7 dias estão cadastrados (`python3 ferramentas/tsp.py agenda --horas 168`). Pesquise SÓ o que falta
   (rodada nova divulgada, fase seguinte do mata-mata, jogo remarcado) e cadastre com `jogo-novo` (ou `remarcar`).
   Confira também, com 1 busca por competição, se algum jogo das próximas 24 horas mudou de dia ou horário.
3. **Competições "verificar"** (uma por dia, a primeira da lista): descubra se ainda há jogos de clube paulista nesta temporada.
   Se sim, mude para "ativa" e cadastre os jogos dos próximos 7 dias; se for de pontos ou grupos, crie dados/base/<chave>.json
   com a classificação atual confirmada em 2 fontes (mesmo formato de dados/base/serie_a.json, com "corte" = agora).
   Se não, mude para "encerrada". Competições "aguardando" (temporada 2027): só verifique às segundas se a tabela já saiu.
4. **Pendentes.** Se `agenda` listar jogos pendentes (já deveriam ter acabado e estão sem resultado), confira agora seguindo
   diretrizes/conferencia.md.
5. **Agendar as conferências do dia.** Rode `python3 ferramentas/tsp.py agenda --horas 24`. Para cada item de "conferencias":
   - chame list_triggers e veja se já existe uma tarefa chamada "TSP · Conferência <conferir_em>"; se existir, pule;
   - senão, crie com create_trigger: name "TSP · Conferência <conferir_em>", run_once_at = conferir_em em RFC3339 com
     -03:00 (ex.: 2026-10-28T21:40:00-03:00), initiation "human_schedule", notifications {} e prompt:
     "Conferência de resultados do TSP. Siga diretrizes/conferencia.md do repositório tudosobrepaulistas/tsp-dados para os jogos <IDs separados por vírgula>."
   - Sem jogos nas próximas 24 h: não crie nada.
6. `python3 ferramentas/tsp.py calcular`, `validar`, commit ("calendário: AAAA-MM-DD") e push.
7. Resumo curto ao dono (SendUserMessage se existir): quantos jogos hoje, horários das conferências, mudanças de calendário,
   competições que mudaram de status, e qualquer problema.
