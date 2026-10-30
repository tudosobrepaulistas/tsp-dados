# Pós-jogo automático (Máquina de Notícias)

Objetivo: assim que um jogo da base termina, publicar uma matéria de resultado para aparecer nas buscas
"<time A> x <time B>", "resultado <time A> x <time B>", "quanto foi o jogo do <time>". Vale para **todos os jogos da base**
(competições com clube paulista, mesmo jogos sem clube paulista, ex.: Grêmio x Athletico-PR na Série A).
O site publica na hora (sem horário fixo) e põe o link "Como foi o jogo" na página do jogo.

## Passo a passo
1. `python3 ferramentas/maquina.py posjogo-pendentes`. Se mostrar `nenhum`, termine.
2. Para cada jogo (o mais antigo primeiro, no máximo 4 por execução):
   - **SEM RESULTADO na base:** procure o placar em 2 fontes independentes (regras do `CLAUDE.md`) e registre com
     `python3 ferramentas/tsp.py resultado ID --placar AxB --fontes URL1 URL2 [--gols ...]`, depois `calcular` e `validar`.
     Fontes discordam ou ainda não publicaram: pule o jogo (a próxima execução tenta de novo).
   - Jogo ainda rolando/atrasado/suspenso: siga as regras 6 e 7 do `CLAUDE.md` e pule.
3. Escreva a matéria com as **2 fontes da crônica do jogo** (podem ser as mesmas do resultado) e o que a base tem
   (gols, classificação depois da rodada em `api/tsp.json`, próximo jogo de cada time). Nada que as fontes não digam.
4. `python3 ferramentas/maquina.py adicionar /tmp/pos.json` → commit e push → `python3 ferramentas/maquina.py avisar-site`.

## Texto (intenção de busca: resultado)
- **Título** com os dois times, o verbo do resultado e o placar por extenso: "Grêmio vence o Athletico-PR por 2 a 0 e ..."
  / "Santos e Palmeiras empatam por 0 a 0 na Vila". A ferramenta exige o placar no título ou subtítulo.
- **1º parágrafo**: placar, competição, rodada/fase, estádio, data e quem fez os gols (só os confirmados).
- Depois: como foi o jogo (1º e 2º tempo, lances decisivos), o que muda na tabela, **próximos jogos** de cada time
  (só se a base ou as fontes confirmarem). Falas pós-jogo só entre aspas, atribuídas e com fonte.
- 1 a 3 `h2` em pergunta: "Quem fez os gols de Grêmio x Athletico-PR?", "Como fica a classificação?", "Qual o próximo jogo do Grêmio?".
- `foco`: "<time A> x <time B>" (ex.: "Grêmio x Athletico-PR"). `meta_title` até 65 com placar. `tags`: os dois times, a competição.
- `faq`: placar, autores dos gols, próximo jogo. `resumo`: 3 frases.
- Sem apostas, sem notas de jogador inventadas, sem estatísticas de bancos de dados.

## Foto
- Se as fontes oficiais dos clubes publicaram foto do jogo com crédito do fotógrafo do clube, use (crédito `Foto: Nome/Clube`).
- Sem isso, mande `"foto_do_jogo": true` e **sem `foto`**: o site usa a foto do estádio da página do jogo (já com crédito).
  Se nem essa existir, a matéria vira rascunho para um redator.

## Formato do JSON
Igual ao de `diretrizes/maquina.md`, com:
```json
{"tipo": "posjogo", "jogo": 91000019, "clube": "", "foto_do_jogo": true, "...": "..."}
```
`clube` pode ficar vazio: a ferramenta preenche com o(s) clube(s) paulista(s) do jogo, se houver.
