public class Main {

    public static void main(String[] args) {

        BlacklistTree blacklist = new BlacklistTree();

        blacklist.insert(192168001001L); // 192.168.1.1
        blacklist.insert(192168001010L); // 192.168.1.10
        blacklist.insert(192168001050L); // 192.168.1.50
        blacklist.insert(172016000010L); // 172.16.0.10
        blacklist.insert(172016000020L); // 172.16.0.20
        blacklist.insert(1000000001L);   // 10.0.0.1

        blacklist.insert(192168001010L);
        blacklist.insert(192168001010L);

        System.out.println("=== BUSCA ===");

        blacklist.search(192168001010L);
        blacklist.search(1000000001L);

        System.out.println("\n=== RELATÓRIO ===");

        blacklist.ordenatedReport();

        System.out.println("\n=== REMOVENDO IP 172.16.0.10 ===");

        blacklist.remove(172016000010L);

        blacklist.ordenatedReport();
    }
}