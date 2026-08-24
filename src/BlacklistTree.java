class BlacklistTree {
    private Node root;

    public void insert(long ip) {
        root = recursiveInsert(root, ip);
    }

    private Node recursiveInsert(Node node, long ip) {
        if (node == null) {
            return new Node(ip);
        }

        if (ip < node.ip) {
            node.left = recursiveInsert(node.left, ip);
        } else if (ip > node.ip) {
            node.right = recursiveInsert(node.right, ip);
        } else{
            node.attemptCounts++;
        }

        return node;
    }

    public boolean search(long ip){
        Node actual = root;

        while (actual != null) {
            if (ip == actual.ip) {
                System.out.println("IP bloqueado: " + actual.ip + " | Tentativas: " + actual.attemptCounts);
                return true;
            }

            if (ip < actual.ip) {
                actual = actual.left;
            } else {
                actual = actual.right;
            }
        }

        System.out.println("IP não está na blacklist.");
        return false;
    }

    public void ordenatedReport() {
        recursiveReport(root);
    }

    private void recursiveReport(Node node) {
        if (node == null) {
            return;
        }

        recursiveReport(node.left);

        System.out.println("IP: " + node.ip + " | Tentativas: " + node.attemptCounts);

        recursiveReport(node.right);
    }

    public void remove(long ip) {
        root = recursiveRemove(root, ip);
    }

    private Node recursiveRemove(Node node, long ip) {
        if (node == null) {
            return null;
        }

        if (ip < node.ip) {
            node.left = recursiveRemove(node.left, ip);
        } 
        else if (ip > node.ip) {
            node.right = recursiveRemove(node.right, ip);
        } 
        else {

            // Caso 1: não possui filhos
            if (node.left == null && node.right == null) {
                return null;
            }

            // Caso 2: possui apenas filho direito
            if (node.left == null) {
                return node.right;
            }

            // Caso 2: possui apenas filho esquerdo
            if (node.right == null) {
                return node.left;
            }

            // Caso 3: possui dois filhos
            Node successor = minorNode(node.right);

            node.ip = successor.ip;
            node.attemptCounts = successor.attemptCounts;

            node.right = recursiveRemove(node.right, successor.ip);
        }

        return node;
    }

    private Node minorNode(Node node) {

        Node actual = node;

            while (actual.left != null) {
                actual = actual.left;
            }

        return actual;
    }
}