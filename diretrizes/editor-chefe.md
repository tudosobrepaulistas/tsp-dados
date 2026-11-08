# Editor-chefe automático (checagem das matérias dos redatores)

Duas vezes por dia. Objetivo: achar **erro de informação** nas matérias publicadas pelos redatores (Paulistão A1, A2, A3,
Série A/B, feminino etc.) comparando com outras fontes, e pedir a correção. A forma (foto, crédito, título, subtítulo,
tamanho) o site já confere sozinho: aqui o foco é o **fato**.

## Passo a passo
1. `python3 ferramentas/correcoes.py listar --horas 14 --max 25` (matérias das últimas 14 horas).
2. Para cada matéria, escolha os **fatos verificáveis**: placar, autor e minuto dos gols, pé/cabeça, adversário,
   data/horário/estádio do próximo jogo, rodada, competição, nome e cargo de quem falou, valores e prazos oficiais.
3. Confira com WebSearch/WebFetch nas fontes aceitas do `CLAUDE.md` (site oficial do clube, FPF, CBF, ge, Lance!,
   Gazeta Esportiva, UOL, jornais da cidade...). Proibido: Sofascore, Flashscore, oGol, Transfermarkt, FotMob,
   placar do Google, e contornar bloqueio/login.
4. Só aponte quando **2 fontes independentes** disserem diferente da matéria (erro grave). Na dúvida, **não aponte**.
   Diferença de opinião, estilo ou detalhe sem importância não é erro.
5. Para cada erro: 
   ```
   python3 ferramentas/correcoes.py apontar ID --gravidade grave \
     --motivo "A matéria diz X; o certo é Y (o gol foi de pé direito, não de esquerdo)" \
     --sugestao "Trocar 'pé esquerdo' por 'pé direito' no 2º parágrafo" \
     --fonte "ge" URL1 --fonte "Site oficial do Clube" URL2
   ```
   `media` para algo sério que não é fato errado (ex.: fala sem atribuição); `leve` não precisa.
6. **Plágio** (regra de 08/11/2026): em cada matéria, pegue 2 ou 3 frases bem específicas (não títulos nem falas entre
   aspas, que podem se repetir) e procure com WebSearch entre aspas. Se outra página tiver **as mesmas frases**
   (cópia literal ou quase, publicada antes) sem crédito, confira abrindo a página e aponte:
   ```
   python3 ferramentas/correcoes.py plagio ID --url URL_DA_PAGINA_COPIADA --nome "Veículo" --trecho "frases iguais"
   ```
   Mesmo assunto com texto diferente **não** é plágio. Fala entre aspas de coletiva ou nota oficial citada com crédito
   também não. Na dúvida, não aponte. O site tira a matéria do ar, trava o redator e avisa o Thiago e o Vinicios na hora.
7. No fim: `git add -A && git commit -m "editor-chefe: N apontamentos"` (com as linhas de coautoria) e `git push`,
   depois `python3 ferramentas/correcoes.py avisar-site`.

## O que acontece no site
O redator recebe a mensagem (painel e e-mail) com o erro, a sugestão e as fontes; o editor-chefe Vinicios Cotrim recebe
a cópia na mesma hora. Prazo: grave 6h, média 24h, leve 48h. Sem correção no prazo, a matéria vira "Recusada" e a
comissão dela não entra no fechamento. Rascunho nunca conta.

Trava: enquanto o redator tiver **qualquer** correção pedida em aberto (erro de informação, de escrita, foto, crédito,
título) ou vencida sem corrigir, ele **não consegue publicar matéria nova**. Corrigiu, libera. Plágio só libera quando
o Thiago ou o Vinicios clicarem em "Liberar redator".

## Tom
Os textos de `--motivo` e `--sugestao` são lidos pelo redator: claros, respeitosos, sem ironia, dizendo o que está errado
e o certo, com o trecho a mudar.
