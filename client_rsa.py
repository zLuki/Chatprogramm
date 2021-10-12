import random
import socket
import json
import threading

def modulares_potenzieren(b,e,m):
    res = 1
    while e > 0:
        if e%2 == 1:
            res = (res*b)%m
        b = (b*b)%m
        e = e//2
    return res


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

# Sucht nach einer Primzahl von n als Startpunkt
def make_prime(n):
    if n%2 == 0:
        n+=1
    while not is_prime(n):
        n+=2
    return n

def decrypt(d, text, N): #decrypt text with d
    text = json.loads(text)
    nums = [int(x, 16) for x in text]
    decrypted = [modulares_potenzieren(x, d, N) for x in nums]
    text = ''.join([chr(x) for x in decrypted])
    return text

def handle(private_key, N, server):
    while True:
        #try:
        text = server.recv(int(1e10)).decode('utf8')
        print("Got message from Server: "+decrypt(private_key, text, N))
        #except:
            #print("FEHLER!")
            #server.close()
            #break

p = make_prime(random.randint(1e100, 1e101))
q = make_prime(random.randint(1e100, 1e101))
N = p*q
phi = (p-1)*(q-1)

# Teilerfremdes e finden
e = make_prime(random.randint(2, phi-1))
while phi % e == 0:
    e = make_prime(random.randint(2, phi-1))

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


#print(e)
#print(N)
#print(private_key)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("10.171.152.171", 50000))

s.send(str(e).encode())
s.send(str(N).encode())

e = int(s.recv(1024).decode())
N_server = int(s.recv(1024).decode())

thread = threading.Thread(target=handle, args=(private_key, N, s))
thread.start()

while (True):
    data = input("Geben Sie die Nachricht ein: ")
    ascii = [ord(x) for x in data]
    encrypted = [modulares_potenzieren(x, e, N_server) for x in ascii]
    hex_nums = [hex(x) for x in encrypted]  
    s.send(json.dumps(hex_nums).encode())