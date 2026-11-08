# Cobertura mínima das Séries A e B (regra das 6 horas)

Os clubes paulistas das Séries A e B (Palmeiras, Santos, São Paulo, Corinthians, Red Bull Bragantino, Mirassol, Novorizontino,
São Bernardo, Botafogo-SP e Ponte Preta; grupo `nacional` em `maquina/clubes.json`) são da redação, mas **nenhum pode
ficar mais de 6 horas sem matéria no site**. Se os redatores não publicarem, a Máquina publica.

## Passo a passo (cada execução)
1. `python3 ferramentas/maquina.py cobertura-6h`. Se mostrar `nenhum`, termine.
2. Para cada clube listado (o mais atrasado primeiro, no máximo 6 por execução):
   - `python3 ferramentas/maquina.py historico CLUBE` (não repetir assunto nem palavra-chave do que o site já tem).
   - Procure **notícia das últimas 24 horas** (site e redes oficiais do clube, ge, Lance!, Gazeta Esportiva, UOL, jornais da
     cidade): treino, coletiva, escalação provável, lesão, contratação, ingresso, arbitragem, bastidores do próximo jogo.
     Fato confirmado em **2 fontes** ou coletiva/comunicado oficial com link. **Nada de evergreen** para estes clubes.
   - Foto real com crédito (site/redes oficiais do clube, miniatura do vídeo oficial no YouTube). Obrigatória.
   - Monte o JSON como em `diretrizes/maquina.md` e rode `python3 ferramentas/maquina.py adicionar /tmp/materia.json`
     (sai em 5 minutos, fora da grade de 30 em 30 minutos e fora da cota diária).
   - Sem notícia confirmada nas últimas 24h: `python3 ferramentas/maquina.py sem-pauta CLUBE --motivo "..." --sugestao "..."`.
3. Commit e push depois de cada matéria (linhas de coautoria) e, no fim, `python3 ferramentas/maquina.py avisar-site`.

As matérias saem pela conta da Máquina e não contam para os redatores.
