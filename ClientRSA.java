import java.math.BigInteger;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Random;
import java.net.*;
import java.io.*;
import java.util.Scanner;

public class ClientRSA {

    private Socket clientSocket;
    private PrintWriter out;
    //private DataOutputStream out;
    //private DataInputStream in;
    private BufferedReader in;

    public static BigInteger modularesPotenzieren(BigInteger b, BigInteger e, BigInteger m) {
        BigInteger res = BigInteger.ONE;
        while (e.compareTo(BigInteger.ZERO) == 1) {
            if (e.remainder(BigInteger.TWO).intValue() == 1) {
                res = res.multiply(b).remainder(m);
                e = e.subtract(BigInteger.ONE);
            }
            b = b.multiply(b).remainder(m);
            e = e.divide(BigInteger.TWO);
        }
        return res;
    }

    private static BigInteger getRandomBigInt(BigInteger min, BigInteger max) {
        BigInteger random;
        Random rand = new Random();
        do {
            random = new BigInteger(max.bitLength(), rand);
        } while (random.compareTo(min) == -1 || random.compareTo(max) == 1);
        return random;
    }

    private static boolean millerRabin(BigInteger n) {
        BigInteger d = n.subtract(BigInteger.ONE);
        BigInteger r = BigInteger.ZERO;
        while (d.remainder(BigInteger.TWO).intValue() == 0) {
            d = d.divide(BigInteger.TWO);
            r = r.add(BigInteger.ONE);
        }
        BigInteger a = getRandomBigInt(BigInteger.TWO, n.subtract(BigInteger.ONE));
        BigInteger x = modularesPotenzieren(a, d, n);
        if (x.compareTo(BigInteger.ONE) == 0 || x.compareTo(n.subtract(BigInteger.ONE)) == 0) {
            return true;
        }
        while (r.compareTo(BigInteger.ONE) == 1) {
            x = modularesPotenzieren(x, x, n);
            if (x.compareTo(BigInteger.ONE) == 0) {
                return false;
            }
            if (x.compareTo(n.subtract(BigInteger.ONE)) == 0) {
                return true;
            }
            r = r.subtract(BigInteger.ONE);
        }
        return false;
    }

    /*  
    Schnelles, aber riskanteres schauen ob n eine Primzahl ist
    Risk 1 = 25% Fehlerwahrscheinlichkeit
    Risk 4 = 0.4% Fehlerwahrscheinlichkeit
    Risk 12 = Ein Fehler ist unwahrscheinlicher als im Lotto zu gewinnen
    Risk 15 = Ein Fehler ist unwahrscheinlicher als zwei mal vom Blitz an einem Tag getroffen zu werden
     */
    private static boolean isPrime(BigInteger n) {
        int RISK = 13, primeTest = 0;
        for (int i = 0; i < RISK; i++) {
            if (millerRabin(n)) primeTest++;
            else primeTest--;
        }
        return primeTest > 0;
    }

    private static BigInteger makePrime(BigInteger n) {
        if (n.remainder(BigInteger.TWO).intValue() == 0) {
            n = n.add(BigInteger.ONE);
        }
        while (!isPrime(n)) {
            n = n.add(BigInteger.TWO);
        }
        return n;
    }

    private static String base36Encoder(BigInteger n) {
        String res = "", chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ";
        BigInteger constant = new BigInteger("36");
        BigInteger[] buf;
        do {
            buf = n.divideAndRemainder(constant);
            res += chars.charAt(buf[1].intValue());
            n = buf[0];
        } while (buf[0].compareTo(BigInteger.ZERO) == 1);
        return new StringBuilder(res).reverse().toString();
    }

    private static BigInteger base36Decoder(String n) {
        String chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ";
        BigInteger sum = BigInteger.ZERO;
        int counter = 0;
        for (int i = n.length()-1; i >= 0; i--) {
            BigInteger posValue = BigInteger.valueOf(36).pow(counter);
            BigInteger numValue = BigInteger.valueOf(chars.indexOf(n.charAt(i)));
            sum = sum.add(posValue.multiply(numValue));
            counter++;
        }
        return sum;
    }

    public void startConnection(String ip, int port) {
        try {
            clientSocket = new Socket(ip, port);
            //out = new DataOutputStream(clientSocket.getOutputStream());
            out = new PrintWriter(clientSocket.getOutputStream(), true);
            //in = new DataInputStream(clientSocket.getInputStream());
            in = new BufferedReader(new InputStreamReader(clientSocket.getInputStream()));
        } catch(IOException e) {
            System.out.println("FEHLER BEIM VERBINDEN MIT DEM SERVER!");
        }
    }

    public void sendMessage(String msg) {
        //try {
            out.println(msg);
            out.flush();
        //} catch (IOException e) {
        //    System.out.println("FEHLER BEIM SENDEN EINER NACHRICHT!");
        //}
        //return;
    }

    public String getMessage() {
        String res = "";
        try {
            while (true) {
                res = in.readLine();
                if (res.length() > 0) break;
            }
        } catch (IOException e) {
            System.out.println("FEHLER BEIM EMPFANGEN EINER NACHRICHT!");
        }
        return res;
    }

    public void stopConnection() {
        try {
            in.close();
            out.close();
            clientSocket.close();
        } catch (IOException e) {
            System.out.println("FEHLER BEIM BEENDEN DER VERBINDUNG ZUM SERVER!");
        }
    }

    public static void main(String[] args) {

        String limit = "1";
        for (int i = 0; i < 10; i++) limit += "0";
        BigInteger min = new BigInteger(limit), max = new BigInteger(limit+"0");

        BigInteger p = makePrime(getRandomBigInt(min, max));
        BigInteger q = makePrime(getRandomBigInt(min, max));
        BigInteger N = p.multiply(q), e;
        BigInteger phi = p.subtract(BigInteger.ONE).multiply(q.subtract(BigInteger.ONE));
        do {
            e = makePrime(getRandomBigInt(BigInteger.TWO, phi.subtract(BigInteger.ONE)));
        } while (e.compareTo(phi) >= 0 || phi.remainder(e).intValue() == 0);

        ArrayList<BigInteger> a = new ArrayList<>(), b = new ArrayList<>();
        
        a.add(phi);
        b.add(e);
        while (b.get(b.size()-1).compareTo(BigInteger.ZERO) != 0) {
            b.add(a.get(a.size()-1).remainder(b.get(b.size()-1)));
            a.add(b.get(b.size()-2));
        }
        ArrayList<BigInteger> y = new ArrayList<>(Arrays.asList(BigInteger.ONE, BigInteger.ZERO, BigInteger.ONE));
        ArrayList<BigInteger> d = new ArrayList<>(Arrays.asList(BigInteger.ZERO, BigInteger.ONE));
        int counter = 3;

        while (counter <= a.size()) {
            d.add(BigInteger.ONE.subtract(y.get(y.size()-1).multiply(a.get(a.size()-counter))).divide(b.get(b.size()-counter)));
            y.add(d.get(d.size()-1));
            counter++;
        }

        BigInteger privateKeyBuf = d.get(d.size()-1);
        if (privateKeyBuf.compareTo(BigInteger.ZERO) < 0) {
            privateKeyBuf = privateKeyBuf.add(a.get(0));
        }
        final BigInteger privateKey = privateKeyBuf;
        //System.out.println(e);
        //System.out.println(N);
        //System.out.println(privateKey);


        ClientRSA client = new ClientRSA();
        client.startConnection("192.168.1.7", 50000);
        client.sendMessage(e.toString());
        client.sendMessage(N.toString());
        
        //System.out.println("Bruder!");
        BigInteger eServer = new BigInteger(client.getMessage());
        BigInteger nServer = new BigInteger(client.getMessage());

        Scanner scanner = new Scanner(System.in);
        String text2 = "Olli";
        String nums2 = "[";
        for (int i = 0; i < text2.length(); i++) {
            int ascii = text2.charAt(i);
            BigInteger encrypted = modularesPotenzieren(BigInteger.valueOf(ascii), eServer, nServer);
            String base36 = base36Encoder(encrypted);
            nums2 += "\""+base36+"\",";
        }
        nums2 = nums2.substring(0, nums2.length()-1) + "]";
        client.sendMessage(nums2);

        //System.out.println(eServer);
        //System.out.println(nServer);
        //System.out.println("Nieder");
        new Thread(() -> {
            while (true) {
                String s = client.getMessage(), text = "";
                //.out.println(s);
                String nums[] = s.substring(s.indexOf("[")+1, s.indexOf("]")).split(",");
                
                for (int i = 0; i < nums.length; i++) {
                    BigInteger encrypted = base36Decoder(nums[i].substring(nums[i].indexOf("\"")+1, nums[i].lastIndexOf("\"")));
                    BigInteger decrypted = modularesPotenzieren(encrypted, privateKey, N);
                    text += String.valueOf((char) (decrypted.intValue()));
                }
                System.out.println("Got message from server: "+text);
            }    
        }).start();
        
        while (true) {
            System.out.print("Geben Sie eine Nachricht ein: ");
            String text = scanner.nextLine();
            String nums = "[";
            for (int i = 0; i < text.length(); i++) {
                int ascii = text.charAt(i);
                BigInteger encrypted = modularesPotenzieren(BigInteger.valueOf(ascii), eServer, nServer);
                String base36 = base36Encoder(encrypted);
                nums += "\""+base36+"\",";
            }
            nums = nums.substring(0, nums.length()-1) + "]";
            client.sendMessage(nums);
        }

    }
}