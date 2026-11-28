# Futebol internacional (28/11/2026, pedido do Thiago)

- Menu "Internacional" por continente: Europa, América do Sul, América do Norte e Central, Ásia, Oceania e África.
  Cada continente mostra as 7 principais ligas e a 8ª opção "Outras ligas" (página /campeonato/<continente>-outras-ligas/).
- Lista das ligas: tema, inc/internacional.php (tsp_int_continentes). Uma "outra liga" só abre (ativa => true) quando um
  jogador que passou pelo futebol paulista vai jogar nela. Liga nova = nova versão do tema; o termo nasce sozinho.
- Matéria internacional: marque a liga em "Campeonatos". Ela ganha sozinha o continente e "futebol-internacional",
  e NÃO aparece na home. Gancho sempre paulista: ex-jogador de clube paulista, rival de paulista, Radar "Paulistas pelo mundo".
- Clube de fora acompanhado (página /times/<slug>/, fora dos blocos paulistas): tema, inc/especial.php (tsp_clubes_fora),
  hoje o Estudiantes. Matéria com o nome dele no título ganha a marcação sozinha.
- Futebol brasileiro (outros estados): mesma lógica, a definir no início dos estaduais de 2027.
- Regras de fonte de sempre (CLAUDE.md). Fontes estrangeiras aceitas: grandes jornais do país (ex.: Olé, Clarín, La Nación,
  El Día de La Plata, Marca, AS, Gazzetta, L'Équipe, A Bola, Record), sites e redes oficiais dos clubes e das ligas.
