# Vídeos dos canais oficiais dos clubes (coletivas, entrevistas, bastidores, gols)

Regra do Thiago (08/11/2026): **toda entrevista e coletiva publicada no YouTube oficial dos clubes que cobrimos vira matéria no TSP**
(a ideia é entrevista: história de torcedor, live de jogo, gols e propaganda **não** entram; a ferramenta já filtra),
com o vídeo do canal oficial dentro da matéria, a miniatura do vídeo como foto ("Foto: Reprodução/YouTube Canal") e o
canal do clube citado. A ideia é levar o conteúdo dos clubes para o portal.

## Passo a passo (cada execução)
1. `python3 ferramentas/maquina.py videos --horas 36`. Se mostrar `nenhum`, vá ao passo 6.
2. Só entrevistas e coletivas (a ferramenta já mostra só elas). No máximo 8 matérias por execução, as mais antigas primeiro.
   **Lugar certo no site** (obrigatório):
   - entrevista do **futebol feminino**: `"clube": "<clube>-feminino"` (ex.: `palmeiras-feminino`), nunca o clube masculino;
   - entrevista da **base**: escreva a categoria no título ("Sub-20", "Sub-17"...): o site leva para o bloco de base;
   - profissional masculino: o clube normal. Assim cada vídeo vai para o bloco certo da home.
3. Para cada vídeo, escreva com o que dá para **confirmar sem inventar**:
   - título e descrição do vídeo (o que a ferramenta mostra) e a miniatura (baixe e olhe a imagem com Read);
   - contexto da base do TSP (último jogo, próximo jogo, tabela: `api/tsp.json`) e de notícias aceitas pelo `CLAUDE.md`;
   - falas entre aspas **só** se uma matéria jornalística aceita ou o texto oficial do clube as reproduzir (link nas fontes).
     Você não assiste ao vídeo: nunca escreva frases que não leu.
   - Título com o nome do clube e o assunto do vídeo (ex.: "Abel fala em coletiva após vitória sobre o Santos: assista").
   - 4 a 6 parágrafos curtos, 1 intertítulo em pergunta, resumo e FAQ.
4. JSON como em `diretrizes/maquina.md`, com:
   ```json
   "tipo": "video",
   "video": {"id": "ID_DE_11_LETRAS", "canal": "TV Palmeiras"},
   "fontes": [{"nome": "TV Palmeiras (YouTube oficial)", "url": "https://www.youtube.com/watch?v=ID"}, ...],
   "foto": {"url": "https://i.ytimg.com/vi/ID/maxresdefault.jpg", "credito": "Foto: Reprodução/YouTube TV Palmeiras",
            "fonte": "https://www.youtube.com/watch?v=ID", "alt": "...", "mostra": "o que a miniatura mostra"}
   ```
   No texto, cite o canal uma vez ("em vídeo publicado no canal oficial do clube, a TV Palmeiras"). O site coloca o vídeo
   logo depois do 1º parágrafo. Matéria de vídeo sai na hora, fora da grade e fora da cota diária.
5. `python3 ferramentas/maquina.py adicionar /tmp/video.json`, commit ("vídeo: <clube> - <assunto>") e push a cada matéria.
6. **Canais que faltam**: a saída lista os clubes sem canal. Em cada execução, cadastre até 5: ache o link do YouTube no
   **site oficial do clube** (rodapé/redes) e rode `python3 ferramentas/maquina.py youtube-canal SLUG URL_DO_CANAL`.
   A ferramenta recusa canal parado há mais de 60 dias. Sem link no site oficial, não cadastre (canal de torcida não vale).
7. No fim: `python3 ferramentas/maquina.py avisar-site`.

## Instagram
Vídeos do Instagram não entram por aqui: o Instagram exige login para ver e não deixa ler a fala do vídeo, e a regra do
TSP proíbe contornar login. Post de Instagram só vale como fonte quando o texto da legenda abre sem login (link exato).
Coletiva que só saiu no Instagram: a redação pode mandar o áudio pela ferramenta de áudio do painel.
