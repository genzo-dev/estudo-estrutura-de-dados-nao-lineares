public class Main {
    public static void main(String[] args){
        // local onde deve ser chamado as métodos e classes para criação da árvore e inserção de seus valores
        BinaryTree tree = new BinaryTree();

        tree.insert(50);
        tree.insert(30);
        tree.insert(80);
        tree.insert(20);
        tree.insert(40);
        tree.insert(70);
        tree.insert(90);

        tree.display();
        tree.qtdNode();
        tree.height();
        tree.qtdLeaf();

    System.out.println("------------------");
        tree.remove(70);
        tree.display();
    System.out.println("------------------");

        tree.remove(50);
        tree.display();
    System.out.println("------------------");

        tree.remove(30);
        tree.display();
    System.out.println("------------------");
            tree.qtdNode();


        tree.remove(10);
        tree.display();
    System.out.println("------------------");

        tree.qtdNode();
    }
}