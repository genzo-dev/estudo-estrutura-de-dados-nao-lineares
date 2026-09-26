# Busca A* (A-Star) vs Greedy Best-First Search (Busca Gulosa)

## Entendendo as Estratégias de Busca

Ambos os algoritmos demonstrados neste projeto utilizam buscas heurísticas. Eles exploram o grid seguindo estratégias matemáticas diferentes para encontrar o caminho do ponto inicial até o destino.

### Algoritmo A* (A-Star)

O A* é focado em encontrar a **rota ótima** (o caminho mais curto possível). Para isso, ele avalia cada passo considerando não apenas o quão perto está do destino, mas também o esforço (custo) que já foi gasto para chegar até ali. Ele desvia de obstáculos de forma inteligente e garante o menor caminho, ao custo de explorar um número maior de nós do que uma busca mais agressiva.

Matematicamente, ele avalia os nós através da função:

> **f(n) = g(n) + h(n)**
> * `g(n)`: Custo exato do ponto inicial até o nó atual.
> * `h(n)`: Estimativa (heurística) de distância do nó atual até o destino.
> 
> **Foco:** Menor custo total `f(n)`.

### Busca Gulosa (Greedy Best-First Search)

A Busca Gulosa é mais agressiva e rápida. Ela toma decisões baseadas puramente na estimativa de distância até o alvo, ignorando o trajeto que já foi percorrido. 

O problema dessa estratégia é que, ao tentar seguir em linha reta para o objetivo, ela frequentemente entra em "becos sem saída" gerados por obstáculos em formato de "U" ou paredes complexas. Como resultado, ela costuma explorar menos nós (sendo mais rápida na execução), mas frequentemente gera rotas subótimas e mais longas.

Matematicamente, ela avalia os nós apenas pela heurística:

> **f(n) = h(n)**
> * `h(n)`: Estimativa (heurística) do nó atual até o destino.
>
> **Foco:** Ficar o mais perto do destino o mais rápido possível, ignorando custos passados.

---

## O Simulador

Este projeto utiliza a biblioteca **Pygame** para criar um ambiente interativo onde é possível construir cenários, executar ambos os algoritmos e comparar visualmente o comportamento e a eficiência de cada estratégia.


### Como rodar

> [!NOTE]
> Requisitos
> 
> Python 3.x
>

1. Prepare o ambiente virtual

```bash
python3 -m venv .venv
```

2. Inicie o ambiente virtual

```bash
# No Windows
.venv\Scripts\activate

# No Linux
source .venv/bin/activate
```

3. Instale a biblitoca pygame
```bash
pip install pygame
```

4. Com o ambiente virtual ativo, rode o simulador
```bash
python3 pathfinder.py
```

### Controles Interativos

* **Botão Esquerdo do Mouse:**
  * 1º Clique: Define o ponto inicial (Laranja).
  * 2º Clique: Define o ponto de destino (Turquesa).
  * Segurar e arrastar: Desenha obstáculos / paredes (Preto).
* **Botão Direito do Mouse:** Apaga o item (ponto ou obstáculo) sob o cursor.
* **Tecla `A`:** Executa o algoritmo **A***.
* **Tecla `G`:** Executa a **Busca Gulosa**.
* **Tecla `C`:** Limpa completamente o cenário e zera o painel de métricas.

### Métricas de Comparação

Ao final da execução de cada algoritmo, o painel inferior exibe os seguintes dados para comparação direta:

1. **Algoritmo utilizado:** (A* ou Busca Gulosa).
2. **Tempo (segundos):** Tempo de processamento até encontrar o destino.
3. **Nós Explorados:** Quantidade de blocos que o algoritmo precisou verificar (demonstra o custo de processamento).
4. **Custo do Caminho:** Quantidade de blocos que compõem a rota final encontrada (demonstra a eficiência da rota).