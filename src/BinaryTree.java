public class BinaryTree {
    private Node root;
    private int acum = 0;

    public BinaryTree(){
        this.root = null; // árvore nasce vazia, posteriormente os valores serão inseridos
    }

    // QUESTÃO 4 - Escreva um algoritmo que insira um número na árvore binária.
    public void insert(int value) {
        // receberá o Nó que foi inserido no método insertNode(Node actual, int value) e irá inserir o valor informado
        this.root = insertNode(this.root, value);
    }

    private Node insertNode(Node actual, int value){
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

    // QUESTÃO 2 - Escreva um algoritmo que conte o número de nós de uma árvore binária.
    public int qtdNode() {
        int total = qtdNode(this.root);
        System.out.println("A árvore possui " + total + " nós.");
        return total;
    }

    private int qtdNode(Node actual) {
        if (actual == null) return 0;
        return 1 + qtdNode(actual.left_node) + qtdNode(actual.right_node);
    }

    // QUESTÃO 1 - Escreva um algoritmo para calcular a altura de um árvore binária.
    public int height() {
        System.out.println("A altura da árvore é de " + height(this.root) + " níveis.");
        return height(this.root);
    }

    private int height(Node actual) {
        if (actual == null) return 0;

        int left = height(actual.left_node);
        int right  = height(actual.right_node);
        return 1 + Math.max(left, right); 
    }

    // QUESTÃO 3 - Escreva um algoritmo que conte o número de folhas de uma árvore binária.
    public int qtdLeaf() {
        System.out.println("A ávore possui " + qtdLeaf(this.root) + " folhas.");
        return qtdLeaf(this.root);
    }

    private int qtdLeaf(Node actual) {
        if (actual == null) return 0;

        if (actual.left_node == null && actual.right_node == null) return 1;
        return qtdLeaf(actual.left_node) + qtdLeaf(actual.right_node);
    }

    // QUESTÃO 5 - Escreva um algoritmo que delete um nó de uma árvore binária.
    public void remove(int value) {
        this.root = removeNode(this.root, value);
    }

    private Node removeNode(Node actual, int value) {
        if (actual == null) {
            System.out.println("O nó " + value + " não foi encontrado");
            return null;
        };
        if (value < actual.node_value) {
            actual.left_node = removeNode(actual.left_node, value);
        } else if (value > actual.node_value) {
            actual.right_node = removeNode(actual.right_node, value);
        } else {
            if (actual.left_node == null && actual.right_node == null) {
                return null;
            }
            if (actual.left_node == null) return actual.right_node;
            if (actual.right_node == null) return actual.left_node;
            Node sucessor = minimo(actual.right_node);
            actual.node_value = sucessor.node_value;
            actual.right_node = removeNode(actual.right_node, sucessor.node_value);
        }
        return actual;
    }

    private Node minimo(Node actual) {
        while (actual.left_node != null) actual = actual.left_node;
        return actual;
    }
}