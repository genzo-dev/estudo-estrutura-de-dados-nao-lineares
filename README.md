# Caixeiro Viajante com Força Bruta e Dijkstra

Projeto didático em Python/Pygame que demonstra o comportamento do Caixeiro
Viajante (TSP) em dois mapas fixos:

- **Mapa de 5 vértices** (`images/brute_force_map.png`): resolvido
  exclusivamente por **força bruta**.
- **Mapa de 18 vértices** (`images/dijkstra_map.png`): resolvido
  exclusivamente com **Dijkstra**.

## O que o programa faz

- Usa os grafos e as posições já definidos em `maps.py`.
- No mapa de 5 vértices, avalia todas as `4! = 24` permutações possíveis,
  descarta as que não têm aresta direta e mantém a rota de menor custo.
- No mapa de 18 vértices, executa Dijkstra a cada passo para encontrar o menor
  caminho até a cidade ainda não visitada mais próxima, montando a rota do
  caixeiro. A força bruta avaliaria `17!` ordens, o que é inviável.
- Permite escolher a cidade inicial clicando em qualquer vértice do grafo.
- Anima a execução: mostra a permutação testada, o melhor custo parcial, os
  caminhos mínimos encontrados pelo Dijkstra e a ordem de visita.
- Diferencia, no painel e no grafo, a **ordem de visita** do **trajeto físico**
  percorrido pelas arestas.
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
vértices. Para cada ordem, verifica se todas as arestas existem e soma os pesos.
A rota fechada de menor custo é mantida. Com 5 vértices são apenas 24 ordens,
então a força bruta é perfeitamente viável.

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
ótima. Já no mapa de 5 vértices, a força bruta garante o ótimo.

Como o trajeto físico usa os menores caminhos do Dijkstra, ele pode passar por
outras cidades intermediárias. Por isso, no mapa grande, um vértice pode
aparecer mais de uma vez no percurso físico, embora a ordem de visita do
caixeiro tenha cada cidade uma única vez.
