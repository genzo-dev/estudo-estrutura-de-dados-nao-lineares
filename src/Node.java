class Node {
    long ip;
    int attemptCounts;
    Node left;
    Node right;

    public Node(long ip) {
        this.ip = ip;
        this.attemptCounts = 1;
        this.left = null;
        this.right = null;
    }
}

