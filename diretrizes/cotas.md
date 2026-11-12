# Cotas diárias por bloco da home (regra do Thiago, 11 e 12/11/2026)

Todo dia o site precisa ter, **contando redação + Máquina**:

| Bloco | Mínimo por dia | Como |
|---|---|---|
| 4 grandes | 1 a cada 1h30 (8h às 23h) | tarefa própria (`diretrizes/grandes.md`) |
| Mirassol + Bragantino | **2 de cada** | 1 de cada até 12h e a 2ª de cada até 18h |
| Série B (paulistas) | **2 de cada clube** | |
| Futebol feminino | **8** | variando entre as 8 equipes do Paulistão Feminino |
| Paulistão A1 (clubes fora das Séries A e B) | **8** | |
| Paulistão A2 | **8** | o clube há mais tempo sem matéria primeiro |
| Paulistão A3 | **8** | idem |
| Paulistão A4 | **8** | idem |
| Clubes sem divisão | **8** | idem |
| Base (masculina e feminina) | **4** | categoria no título: Sub-20, Sub-17, Sub-15... |

Se a redação não fez, a Máquina faz. A Máquina nunca passa da conta: só completa o que falta.

## Passo a passo (tarefa "Cotas do dia": 11h43, 17h43 e 21h43)

1. `python3 ferramentas/maquina.py cotas`. Ele conta o que saiu hoje no site e diz quanto falta **agora**
   (a meta cresce ao longo do dia; às 21h vale a meta cheia). Se disser "tudo em dia", termine.
2. Ordem: Mirassol + Bragantino → Série B → base → A1 → A2 → A3 → feminino → A4 → sem divisão.
   No máximo **14 matérias por execução**. Em cada bloco use os clubes listados, na ordem (o mais esquecido primeiro),
   e PRIMEIRO as pautas que aparecem embaixo de cada um (abra os links).
3. Conteúdo, nesta ordem: notícia das últimas 48h confirmada em 2 fontes → coletiva/nota oficial com link →
   (só A2, A3, A4, sem divisão e feminino) evergreen bem apurado dentro dos limites do `adicionar`
   (estádio, ídolos, títulos, rivalidades, como o clube está hoje para 2027). Mirassol, Bragantino, Série B e A1:
   só notícia ou coletiva. Base: jogos, convocações, renovações e destaques das categorias, confirmados.
4. Mesmas regras de sempre (`diretrizes/maquina.md`): foto real com crédito, olhada (Read), `foto.mostra` honesto;
   fontes no rodapé; nada inventado; nada de apostas; sem repetir assunto (`maquina.py historico CLUBE`).
5. Horário: `"publish_at"` = agora + 5 min, somando 3 min a cada matéria seguinte (dois itens não podem ter o mesmo
   horário). Mirassol/Bragantino na execução das 11h43: `publish_at` 12:00 e 12:03; na das 17h43: 18:00 e 18:03.
6. Depois de cada matéria: `python3 ferramentas/maquina.py adicionar /tmp/materia.json`, commit
   ("máquina: cota - <bloco> - <clube> - <assunto>") e push. No fim: `python3 ferramentas/maquina.py avisar-site`.
7. Sem notícia nem evergreen possível para um clube: `maquina.py sem-pauta CLUBE --motivo ... --sugestao ...` e passe ao próximo.
8. Resumo: placar de cada bloco no fim (rode `cotas` de novo) e o que não deu e por quê.
