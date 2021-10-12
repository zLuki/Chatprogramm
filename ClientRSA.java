import java.math.BigInteger;
import java.util.Random;

public class ClientRSA {

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
        int RISK = 12;
        for (int i = 0; i < RISK; i++) {
            if (!millerRabin(n)) return false;
        }
        return true;
    }

    /*private static BigInteger makePrime(BigInteger n) {
        if (n.remainder(BigInteger.TWO).intValue() == 0) {
            n = n.add(BigInteger.ONE);
        }
        while (!isPrime(n)) {
            n = n.add(BigInteger.TWO);
        }

        return BigInteger.ZERO;
    }*/

    public static void main(String[] args) {
        BigInteger b = new BigInteger("7"), e = new BigInteger("64"), N = new BigInteger("43");
        int c = 0;
        for (int i = 0; i < 1000; i++) {
            if (millerRabin(b)) c++;
        }
        System.out.println(c);
    }
}


/*def modulares_potenzieren(b,e,m):
    res = 1
    while e > 0:
        if e%2 == 1:
            res = (res*b)%m
        b = (b*b)%m
        e = e//2
    return res*/