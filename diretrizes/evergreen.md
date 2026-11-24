# Evergreen diário dos clubes sem divisão (24/11/2026, pedido do Thiago)

Meta: **6 textos atemporais por dia** dos 41 clubes sem divisão, pelas buscas que mais trazem gente ao TSP.
A varredura das buscas foi feita UMA vez (Search Console, 16 meses, em 24/11/2026) e virou `dados/pautas_evergreen.json`
(246 pautas: 6 temas por clube, clubes mais buscados primeiro). Não refaça a varredura a cada execução.

## O que o Search Console mostrou
- Quem procura esses clubes busca pelo **nome do clube** ("ranchariense fc", "ibrachina", "batatais futebol clube"): falta uma página que responda "quem é esse clube".
- Também procuram **estádio** ("estádio araçatuba", "estádio do guaratinguetá") e **sub-20/Copinha** (Audax, Ibrachina, Itaquaquecetuba, Flamengo de Guarulhos, União Mogi).
- Mais buscados: Araçatuba, Audax, Itaquaquecetuba, Ibrachina, Nacional, Assisense, Paulínia, Centro Olímpico, Ranchariense e Matonense.

## Temas (ordem de prioridade)
1. **historia:** quem é o clube, fundação, cidade, cores, títulos e acessos com ano. Palavra-chave: "<clube> futebol clube".
2. **estadio:** nome oficial e popular, capacidade, endereço, como chegar.
3. **copinha:** participações na Copa São Paulo, campanhas da base e jogadores revelados.
4. **idolos:** quem já vestiu a camisa e ídolos da torcida.
5. **rival:** clássicos e rivalidades regionais.
6. **hoje:** divisão, diretoria e planos para 2027 (só com fonte recente).

## Cada execução
1. `python3 ferramentas/maquina.py evergreen` mostra as pautas do dia (uma por clube; pula clube com matéria histórica nos últimos 6 dias).
2. Para cada uma, rode `python3 ferramentas/maquina.py historico CLUBE`. Se o site já tem esse tema, não repita: `evergreen --pular ID --motivo "site já tem"` e pegue a próxima.
3. Apure com fonte (site oficial, FPF, CBF, jornais da cidade, ge, Gazeta Esportiva; Wikipédia só como pista). Título, ano e número sem fonte ficam fora.
   Tema sem fonte segura: `evergreen --pular ID --motivo "..."`.
4. JSON no formato de `diretrizes/maquina.md`, com `"tipo": "historia"` e `"pauta_evergreen": "<id>"`. Foto: estádio ou time com crédito (Commons CC BY/CC BY-SA, site oficial).
   Sem foto conferida, `foto_pendente`. Chefe de Redação antes do `adicionar` (diretrizes/chefe-de-redacao.md).
5. `adicionar` marca a pauta como feita. Commit e push depois de cada matéria. No fim, `avisar-site`.
