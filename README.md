# Caixeiro Viajante com Dijkstra e Caixeiro Viajante Clássico

Projeto didático em Python que demonstra soluções para o problema do Caixeiro Viajante (Traveling Salesman Problema — TSP) com Dijktra e sem.

## O que o programa faz

- Gera um grafo aleatório **conexo** com 5 a 10 vértices.
- Cada aresta tem um peso positivo e o grafo é não direcionado.
- Permite escolher a quantidade de vértices usando os botões `+` e `−`.
- Oferece **dois modelos de TSP**, escolhidos em um seletor no topo:
  - **TSP + Dijkstra**: o Dijkstra calcula as menores distâncias entre todos os pares e o TSP usa essa matriz (pode passar por cidades intermediárias).
  - **TSP Clássico**: visita única, apenas arestas diretas (o Dijkstra **não** é usado).
- Trocar o modelo gera um **novo grafo** adequado a ele. No modo clássico o grafo tem um **ciclo hamiltoniano garantido**.
- Executa Dijkstra a partir de cada vértice para calcular as menores distâncias entre todos os pares (apenas no modelo "TSP + Dijkstra").
- Usa essa matriz de distâncias mínimas para resolver o TSP por força bruta.
- O grafo é **sempre conexo**: a geração parte de uma árvore aleatória e há uma verificação defensiva que garante que nenhuma componente fique isolada.
- Mostra progresso, vértices processados, quantidade de vértices e arestas, tempos e custo total.
- Diferencia, no painel e no grafo, a **ordem de visita** (decisão do TSP) do **trajeto físico** percorrido (menores caminhos do Dijkstra).

## Como executar

> [!Note]
>
> Requisitos:
> 
> - Python 3.10 ou superior recomendado
> - Pygame

Abra o terminal na pasta do projeto e execute:

```bash
python -m venv .venv
```

Ative o ambiente virtual.

**Linux/macOS:**
```bash
source .venv/bin/activate
```

**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

Instale a dependência e execute:

```bash
pip install -r requirements.txt
python main.py
```

## Como usar

1. Ao abrir, o programa gera um grafo aleatório.
2. Escolha o **modelo** no seletor no topo: **"TSP + Dijkstra"** ou **"TSP Clássico"**. Trocar de modelo gera um novo grafo.
3. Use `+` ou `−` para escolher entre 5 e 10 vértices.
4. Clique em **Novo grafo** para trocar o grafo mantendo a mesma quantidade de vértices.
5. Clique em **Iniciar execução** (ou pressione **ESPAÇO**). No modelo "TSP + Dijkstra" roda o Dijkstra e depois o TSP; no "TSP Clássico" roda apenas o TSP.
6. No painel aparecem o custo total e **duas listas**: a *ordem de visita* (decisão do TSP) e o *trajeto no grafo* (caminho físico). O trajeto é destacado em verde com setas, e cada cidade recebe um selo roxo com sua ordem de visita.

No modelo **"TSP + Dijkstra"**, o painel também mostra uma linha de comparação
com o custo do **TSP Clássico** no mesmo grafo (ou avisa que é inviável). Se o TSP
clássico não tiver nenhuma rota válida, aparece um aviso de inviabilidade.

Durante a execução, a etapa atual fica destacada no topo, as barras de progresso mostram o andamento de cada algoritmo e o **melhor custo parcial** aparece em tempo real enquanto o TSP avalia as permutações.


#### Exemplo da execução do Caixeiro Viajante com Dijkstra

![TSP com Dijkstra](/images/ex_tsp_dijkstra.png)
_Figura 1 - TSP + Dijkstra_

#### Exemplo da execução do Caixeiro Viajante Clássico

![TSP Clássico](/images/ex_tsp_classic.png)
_Figura 2 - TSP Clássico_

## Como os algoritmos trabalham juntos

### Dijkstra

Dijkstra calcula o menor custo entre uma origem e cada vértice alcançável. O programa executa Dijkstra uma vez para cada vértice, construindo uma matriz de distâncias mínimas.

### Caixeiro Viajante (TSP)

O TSP mantém o vértice inicial fixo e testa todas as permutações dos outros vértices. Para cada ordem, soma as distâncias, incluindo o retorno à origem, e mantém a rota de menor custo. Há duas variantes:

- **TSP + Dijkstra** (`solve_tsp`): soma os **menores caminhos** da matriz do Dijkstra, podendo passar por cidades intermediárias.
- **TSP Clássico** (`solve_tsp_classic`): soma as **arestas diretas** do grafo e descarta ordens sem aresta direta, produzindo um ciclo hamiltoniano (visita única). Se não existir nenhuma ordem válida, o resultado é marcado como inviável.

Como há no máximo 10 vértices, a força bruta é viável para este exercício: com 10 vértices, são avaliadas `9! = 362.880` ordens (cerca de 2 s no modo "TSP + Dijkstra"). A partir de 11 vértices o brute force deixa de ser viável.

#### Sobre o Ciclo Hamiltoniano

**O que é o Ciclo Hamiltoniano?**

Na teoria matemática dos grafos, um ciclo hamiltoniano é um caminho contínuo e fechado que visita cada nó (ou cidade) de um mapa exatamente uma vez e, ao final, retorna obrigatoriamente ao ponto de partida.

**Por que ele é necessário para o TSP Clássico?**

- **Define as Regras de uma Rota Válida**: A exigência básica do TSP — visitar todas as cidades sem repetir nenhuma e voltar à origem — é a definição literal de um ciclo hamiltoniano. Sem esse conceito, o problema não teria regras matemáticas claras sobre o que constitui uma solução aceitável.

- **Pré-requisito de Viabilidade**: Antes de se preocupar em calcular a rota mais rápida ou barata (otimização), é necessário garantir matematicamente que é possível conectar todos os pontos sem quebras (decisão). Se um mapa não permite a formação de um ciclo hamiltoniano, o TSP é insolúvel para ele.

- **A Essência do Problema**: Em resumo, o TSP clássico nada mais é do que o desafio prático e computacional de analisar os ciclos hamiltonianos de um grafo para descobrir qual deles possui o menor custo total (menor distância, tempo ou dinheiro).

## Limitação conceitual importante

Dijkstra **não elimina a complexidade combinatória do TSP**. Ele calcula eficientemente os menores caminhos entre pares de vértices; o TSP ainda precisa escolher a melhor ordem de visita.

No modelo **"TSP + Dijkstra"** o TSP é resolvido sobre a **matriz de distâncias mínimas**. Ao expandir a rota final no grafo original, um caminho mínimo entre duas cidades pode passar por outros vértices intermediários, então esses vértices podem aparecer fisicamente no percurso mais de uma vez. Isso é esperado nesse modelo.

Já no modelo **"TSP Clássico"** a rota usa apenas arestas diretas e cada cidade é visitada uma única vez (ciclo hamiltoniano), então não há repetição de vértices.