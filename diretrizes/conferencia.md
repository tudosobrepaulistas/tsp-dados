# Conferência de resultados (roda 2h10 depois do início dos jogos)

1. Repositório: add_repo (owner "tudosobrepaulistas", repo "tsp-dados", access "push"), clone, leia CLAUDE.md.
2. Para cada ID recebido (e para os "pendentes" de `python3 ferramentas/tsp.py agenda`):
   - Pesquise o resultado como um jornalista: WebSearch "<mandante> x <visitante> <dd/mm/aaaa> placar" e abra 2 matérias
     de fontes diferentes (lista de fontes aceitas no CLAUDE.md). Anote placar, autores e minutos dos gols, pênaltis.
   - **Encerrado e as 2 fontes batem:** `python3 ferramentas/tsp.py resultado ID --placar 2x1 --fontes URL1 URL2 --gols "..."`.
   - **Ainda em andamento / atrasou / sem matéria ainda:** `ocorrencia ID --status atrasado --obs "..."` e marque para reconferir.
   - **Suspenso, adiado, cancelado:** `ocorrencia ID --status ... --obs "o que aconteceu" [--parcial AxB --minuto M]`.
   - **Fontes discordam:** não registre; marque para reconferir.
3. `calcular`, `validar`, commit ("resultado: ...") e push.
4. **Reconferir:** se sobrou algum ID para reconferir e esta já é a 4ª tentativa (veja no nome da tarefa), pare e avise.
   Senão, crie com create_trigger uma tarefa única para daqui a 30 minutos: name "TSP · Conferência <AAAA-MM-DD HH:MM> (tentativa N+1)",
   run_once_at = agora + 30 min em RFC3339 -03:00, initiation "human_schedule", notifications {}, prompt
   "Conferência de resultados do TSP. Siga diretrizes/conferencia.md do repositório tudosobrepaulistas/tsp-dados para os jogos <IDs que faltam>."
5. Resumo de 1 a 3 linhas: o que entrou (placares), o que ficou para reconferir e por quê.
