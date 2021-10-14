import random
import socket
import socket, threading
import json
import numpy
import re

# MillerRabin Algorithmus
def millerRabin(n):
    d = n-1
    r = 0
    while d%2 == 0:
        d//=2
        r+=1
    a = random.randint(2, n-1)
    x = modulares_potenzieren(a, d, n)
    if x == 1 or x == n-1:
        return True
    while r > 1:
        x = modulares_potenzieren(x, x, n)
        if x == 1:
            return False
        if x == n-1:
            return True
        r -= 1
    return False

# Schnelles, aber riskanteres schauen ob n eine Primzahl ist
# Risk 1 = 25% Fehlerwahrscheinlichkeit
# Risk 4 = 0.4% Fehlerwahrscheinlichkeit
# Risk 12 = Ein Fehler ist unwahrscheinlicher als im Lotto zu gewinnen
# Risk 15 = Ein Fehler ist unwahrscheinlicher als zwei mal vom Blitz an einem Tag getroffen zu werden
def is_prime(n):
    risk = 12
    for i in range(risk):
        if not millerRabin(n):
            return False
    return True

def make_prime(n):
    while (is_prime(n) == False):
        n+=1
    return n

def search_e(phiN):
    #search number e -> 1<e<phiN, ggT(e,phiN) = 1
    #e as prime number, so they cant have the same divider
    while(1):
        e=make_prime(random.randint(2, phiN-1))
        if(phiN % e != 0):
            return e

def modulares_potenzieren(b,e,m):
    res=1
    while e>0:
        if(e%2==1):
            res = (res*b)%m
        b=(b*b)%m
        e=e//2
    return res

def broadcast(message):                                                 #broadcast funktion
    ascii = [ord(x) for x in message]
    for i in range(len(clients)):
        encrypted = [modulares_potenzieren(x, int(public_keys[i][0]), int(public_keys[i][1])) for x in ascii]
        base36_nums = [numpy.base_repr(x, base=36) for x in encrypted]
        clients[i].send((json.dumps(base36_nums)+"\r\n").encode())


def handle(client, d):
    while True:
        try:                                                            #recieving messages vom Client
            text = client.recv(int(1e10)).decode('utf8')
            print("Client "+str(clients.index(client)) + ": " +decrypt(private_key, text, N))
            broadcast(decrypt(private_key, text, N))
        except:
            print("Client " + str(clients.index(client)) + " disconnected.")                                                    #löschen der Clients
            index = clients.index(client)
            public_keys.pop(index)
            clients.remove(client)
            client.close()
            break

def receive(e, N, private_key):                                                          #mehrere Clients empfangen
    while True:
        client, address = server.accept()
        print("Verbunden mit {}".format(str(address)))
        e_client = re.sub("\D", "", client.recv(1024).decode('utf8'))
        N_client = re.sub("\D", "", client.recv(1024).decode('utf8'))
        print(e_client)
        print(N_client)
        public_keys.append([e_client, N_client])
        client.send((str(e)+"\r\n").encode('utf8'))
        client.send((str(N)+"\r\n").encode('utf8'))
        clients.append(client)
        thread = threading.Thread(target=handle, args=(client, private_key))
        thread.start()

def decrypt(d, text, N): #decrypt text with d
    text = json.loads(text)
    nums = [int(x, 36) for x in text]
    decrypted = [modulares_potenzieren(x, d, N) for x in nums]
    text = ''.join([chr(x) for x in decrypted])
    return text


if __name__ == "__main__":
    print("RSA Start")

    p = make_prime(random.randint(1e100, 1e101))
    q = make_prime(random.randint(1e100, 1e101))
    N = p*q
    phi = (p-1)*(q-1)

    # Teilerfremdes e finden
    e = make_prime(random.randint(2, phi-1))
    while phi % e == 0:
        e = make_prime(random.randint(2, phi-1))

    #p und e an client senden


    # erweiterter euklidischer Algorithmus
    a, b, q = [phi], [e], []
    while b[-1] != 0:
        q.append(a[-1]//b[-1])
        b.append(a[-1]%b[-1])
        a.append(b[-2])

    y, d, counter = [1, 0], [0, 1], -2
    while -counter <= len(a):
        d.append(-(y[-1]*a[counter]-1) // b[counter])
        y.append(d[-1])
        counter -= 1

    # Falls der private key negativ ist, muss noch einmal das a addiert werden
    private_key = d[-1] if d[-1] > 0 else d[-1] + a[0]

    host = '192.168.48.129'                                                   #LocalHost
    port = 50000                                                             #Port wählen

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)              #socket initialisieren
    server.bind((host, port))                                               #binding host und port zu einem socket
    server.listen()

    clients = []
    public_keys = []
    nicknames = ["WDQAD"]
    nicknames[0] = "ewqdq"
    print("RSA_FINISHED")
    receive(e, N, private_key)





