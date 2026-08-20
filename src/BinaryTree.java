public class BinaryTree {
    private Node root;
    private int acum = 0;

    public BinaryTree(){
        this.root = null; // árvore nasce vazia, posteriormente os valores serão inseridos
    }

    public void insert(int value) {
        // QUESTÃO 4 - Escreva um algoritmo que insira um número na árvore binária.

        // receberá o Nó que foi inserido no método insertNode(Node actual, int value) e irá inserir o valor informado
        this.root = insertNode(this.root, value);
        acum += 1;
    }

    private Node insertNode(Node actual, int value){
        // QUESTÃO 4 - Escreva um algoritmo que insira um número na árvore binária.

        // receberá o novo Nó e seu valor, depois retornará para ser utilizado no método insert(int value)
        if (actual == null) {
            return new Node(value); // nesse caso a árvore ainda não foi criada, logo, o primeiro nó será a raiz
        }

        if (value < actual.node_value) {
            actual.left_node = insertNode(actual.left_node, value); // caso o valor seja menor que o valor do nó atual, acrescentamos do lado esquerdo
        } else if (value > actual.node_value) {
            actual.right_node = insertNode(actual.right_node, value); // caso o valor seja maior que o valor do nó atual, acrescentamos do lado direito
        }

        return actual;
    }

    public void display() {
        display(this.root, 0);
    }

    private void display(Node actual, int nivel) {
        if (actual == null) return;
    
        display(actual.right_node, nivel + 1);
        System.out.println("  ".repeat(nivel) + actual.node_value);
        display(actual.left_node, nivel + 1);
    }

    public void qtdNode() {
        // QUESTÃO 2 - Escreva um algoritmo que conte o número de nós de uma árvore binária.
        System.out.println("A árvore possui " + acum + " nós.");
    }

    public int height() {
        // QUESTÃO 1 - Escreva um algoritmo para calcular a altura de um árvore binária.
        System.out.println("A altura da árvore é de " + height(this.root) + " níveis.");
        return height(this.root);
    }

    private int height(Node actual) {
        // QUESTÃO 1 - Escreva um algoritmo para calcular a altura de um árvore binária.
        if (actual == null) return 0;

        int left = height(actual.left_node);
        int right  = height(actual.right_node);
        return 1 + Math.max(left, right); 
    }

    public int qtdLeaf() {
        // QUESTÃO 3 - Escreva um algoritmo que conte o número de folhas de uma árvore binária.
        System.out.println("A ávore possui " + qtdLeaf(this.root) + " folhas.");
        return qtdLeaf(this.root);
    }

    private int qtdLeaf(Node actual) {
        // QUESTÃO 3 - Escreva um algoritmo que conte o número de folhas de uma árvore binária.
        if (actual == null) return 0;

        if (actual.left_node == null && actual.right_node == null) return 1;
        return qtdLeaf(actual.left_node) + qtdLeaf(actual.right_node);
    }
}