# 4 grandes a cada 1h30 (Palmeiras, Corinthians, São Paulo e Santos)

Regra do Thiago (09/11/2026): das 8h às 23h, o site não pode ficar mais de 1h30 sem matéria de um dos 4 grandes.
Se a redação não publicou, a Máquina publica.

1. `python3 ferramentas/maquina.py grandes`. Se disser "em dia", termine.
2. Escreva **1 matéria** do clube mais esquecido (o primeiro da lista), usando primeiro as pautas que aparecem embaixo
   dele (abra os links; 2 fontes ou nota/coletiva oficial com link). Sem pauta útil, procure notícia das últimas 24h
   (site e redes oficiais, ge, Lance!, Gazeta Esportiva, UOL, Terra, CNN): treino, coletiva, lesão, contratação,
   ingresso, arbitragem, bastidores do próximo jogo. Nada de evergreen. Não repita assunto que o site já tem
   (`maquina.py historico CLUBE`): se a pauta já virou matéria, ache um ângulo novo e real ou passe ao próximo clube.
3. Foto real com crédito, olhada antes de usar (Read), `foto.mostra` honesto; fontes no rodapé (campo `fontes`).
4. JSON como em `diretrizes/maquina.md` (`"pauta": "<id da pauta>"` quando usar uma) →
   `python3 ferramentas/maquina.py adicionar /tmp/materia.json` (clube da redação: sai em 5 minutos, fora da cota),
   commit ("máquina: 4 grandes - <clube> - <assunto>") e push, depois `python3 ferramentas/maquina.py avisar-site`.
