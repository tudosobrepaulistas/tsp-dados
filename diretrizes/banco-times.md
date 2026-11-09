# Banco de times (elencos e escalações) — páginas /time/<time>/ e "Números da temporada"

Pedido do Thiago (08/11/2026): páginas de time ricas (números da temporada, últimos jogos, artilheiros, jogadores mais
utilizados com campinho, elenco) para TODOS os times que enfrentam clubes paulistas. Tudo vem da base própria do TSP.
**Proibido copiar bancos de estatística** (oGol/zerozero, Sofascore, Flashscore, Transfermarkt, FotMob, FootyStats, BeSoccer...).

## 1. Escalações confirmadas (o que alimenta "mais utilizados" e o campinho)
`python3 ferramentas/tsp.py jogos-sem-escalacao --dias 10` lista os jogos encerrados sem escalação.
Para cada um, ache a **ficha técnica** numa fonte aceita (Gazeta Esportiva, Lance!, ge, UOL, Terra, site oficial do clube,
CBF/FPF) e grave:
```
python3 ferramentas/tsp.py escalacao ID --json /tmp/esc.json
{"casa": {"tecnico": "Abel Ferreira", "time": "Weverton; Giay, Gustavo Gómez, Murilo, Piquerez; Aníbal, Andreas; Felipe Anderson, Vitor Roque, Facundo Torres",
          "entraram": [{"jogador": "Maurício", "saiu": "Andreas", "minuto": "60"}]},
 "fora": {...}, "fontes": ["https://link-exato-da-ficha"]}
```
- Linhas do campo separadas por ";" na ordem goleiro → defesa → meio → ataque, como a ficha publica (é isso que desenha
  o campinho). Nomes como a fonte escreve (o mesmo nome usado nos gols da base, para somar certo).
- Substituições só se a fonte trouxer; sem minuto, deixe "minuto" vazio. Nada de suposição: sem ficha, pule o jogo.

## 2. Elencos (site oficial do clube)
`python3 ferramentas/tsp.py elencos-faltando` lista os times sem elenco ou com elenco de mais de 30 dias (quem joga
antes vem primeiro). Abra a página **Elenco** do **site oficial** do clube e grave:
```
python3 ferramentas/tsp.py elenco CHAVE --json /tmp/elenco.json
{"fonte": "https://site-oficial/elenco", "jogadores": [{"nome": "Weverton", "posicao": "Goleiro", "numero": 21}, ...]}
```
posicao: Goleiro, Zagueiro, Lateral, Volante, Meia, Atacante (meia-atacante = Meia; ponta = Atacante). Número só se o
site mostrar. Site oficial sem elenco ou bloqueado: pule o time (não use outra fonte).

## 3. Fim
`python3 ferramentas/tsp.py calcular && python3 ferramentas/tsp.py validar`, commit ("banco de times: N escalações,
M elencos") e push no main. O site atualiza as páginas sozinho.
