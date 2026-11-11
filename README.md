# Caixeiro Viajante com Força Bruta e Dijkstra

Projeto didático em Python/Pygame que demonstra o comportamento do Caixeiro
Viajante (TSP) em dois mapas fixos:

- **Mapa de 5 vértices** (`images/brute_force_map.png`): resolvido
  exclusivamente por **força bruta**, incluindo o cálculo dos caminhos mínimos
  por busca exaustiva.
- **Mapa de 18 vértices** (`images/dijkstra_map.png`): resolvido
  exclusivamente com **Dijkstra**.

## O que o programa faz

- Usa os grafos e as posições já definidos em `maps.py`.
- No mapa de 5 vértices, calcula os menores caminhos entre todos os pares por
  busca exaustiva (sem usar Dijkstra) e depois avalia todas as `4! = 24`
  permutações possíveis, mantendo a rota de menor custo.
- No mapa de 18 vértices, executa Dijkstra a cada passo para encontrar o menor
  caminho até a cidade ainda não visitada mais próxima, montando a rota do
  caixeiro. A força bruta avaliaria `17!` ordens, o que é inviável.
- Permite escolher a cidade inicial clicando em qualquer vértice do grafo.
- Anima a execução: mostra a permutação testada, o melhor custo parcial, os
  caminhos mínimos encontrados e a ordem de visita.
- Diferencia, no painel e no grafo, a **ordem de visita** do **trajeto físico**
  percorrido pelas arestas. O trajeto pode usar cidades intermediárias nos dois
  mapas.
- Mostra progresso, tempo, custo total e a rota final destacada com setas.

## Como executar

> [!Note]
>
> Requisitos:
>
> - Python 3.10 ou superior recomendado
> - Pygame

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

No Windows (PowerShell), ative o ambiente com:

```powershell
.venv\Scripts\Activate.ps1
```

## Como usar

1. Escolha o mapa no seletor do topo: **Força bruta (5)** ou **Dijkstra (18)**.
2. Clique em uma cidade do grafo para definir o ponto de partida.
3. Clique em **Iniciar execução** ou pressione **ESPAÇO**.
4. Acompanhe as barras de progresso, a rota em construção e o custo parcial.
5. Ao terminar, a melhor rota aparece em verde, com a ordem de visita nos selos
   roxos e o trajeto físico destacado por setas.
6. Use **Reiniciar** para limpar o resultado mantendo o mapa e o início atuais.

## Como os algoritmos trabalham

### Força bruta (5 vértices)

O vértice inicial fica fixo e o programa testa todas as permutações dos demais
vértices. Para cada ordem, soma os menores custos entre as cidades e mantém a
rota fechada de menor custo. Com 5 vértices são apenas 24 ordens, então a força
bruta é perfeitamente viável.

Antes das permutações, o programa calcula os menores caminhos entre todos os
pares enumerando os caminhos simples do grafo. A decisão é tomada **por trecho**,
ao avaliar cada par `A→B`:

- se o caminho com cidade intermediária for mais barato, ele é usado;
- se o custo for igual ao da aresta direta, o caminho direto é mantido;
- se o intermediário for mais caro, o caminho direto é mantido.

Por exemplo, `3→4` custa `6` via `3→5→4`, em vez de `7` pela aresta direta. Já a
permutação `1→2→3→4→5→1` é avaliada com o trajeto físico
`1→2→3→5→4→5→1`, pois o trecho `3→4` usa `5` como intermediário. Neste mapa,
porém, o ótimo encontrado é `1→2→3→5→4→1`, que já usa apenas arestas diretas.

### Dijkstra (18 vértices)

Dijkstra calcula o menor caminho de uma origem até todos os vértices
alcançáveis. No mapa grande, o programa usa Dijkstra a cada trecho para:

1. calcular as menores distâncias a partir da cidade atual;
2. escolher a cidade ainda não visitada mais próxima;
3. reconstruir o caminho mínimo até ela;
4. repetir o processo até visitar todas as cidades e retornar ao início.

Com 18 vértices, a força bruta testaria `17! ≈ 3,5 × 10^14` ordens. Por isso o
mapa grande usa apenas Dijkstra.

## Limitação conceitual importante

Dijkstra **não elimina a complexidade combinatória do TSP**. Ele calcula
eficientemente os menores caminhos entre cidades; no mapa de 18 vértices, a
ordem de visita é construída pela estratégia do vizinho mais próximo guiada pelo
Dijkstra. Essa estratégia é rápida e demonstrativa, mas não garante a rota
ótima. Já no mapa de 5 vértices, a força bruta garante o ótimo considerando os
caminhos intermediários permitidos.

Como o trajeto físico usa os menores caminhos entre as cidades, ele pode passar
por outras cidades intermediárias nos dois mapas. Por isso, um vértice pode
aparecer mais de uma vez no percurso físico, embora a ordem de visita do
caixeiro tenha cada cidade uma única vez.
