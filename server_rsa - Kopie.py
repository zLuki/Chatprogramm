import random
import socket
import socket, threading
import json
import numpy
import re
import tkinter as tk
from tkinter import *
import time
from PIL import Image, ImageTk
from stoppable_thread import Stoppable_thread

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

def broadcast(message, public_keys, clients):                                                 #broadcast funktion
    ascii = [ord(x) for x in message]
    for i in range(len(clients)):
        encrypted = [modulares_potenzieren(x, int(public_keys[i][0]), int(public_keys[i][1])) for x in ascii]
        base36_nums = [numpy.base_repr(x, base=36) for x in encrypted]
        clients[i].send((json.dumps(base36_nums)+"\r\n").encode())
        print("Hoi")

def decrypt(d, text, N): #decrypt text with d
    text = json.loads(text)
    nums = [int(x, 36) for x in text]
    decrypted = [modulares_potenzieren(x, d, N) for x in nums]
    text = ''.join([chr(x) for x in decrypted])
    return text

def handle(client, private_key, N, public_keys, clients):
    while True:
        try:                                                            #recieving messages vom Client
            text = client.recv(int(1e6)).decode('utf8')
            print("Client "+str(clients.index(client)) + ": " +decrypt(private_key, text, N))
            broadcast(decrypt(private_key, text, N), public_keys, clients)
        except:
            print("Client " + str(clients.index(client)) + " disconnected.")                                                    #löschen der Clients
            index = clients.index(client)
            public_keys.pop(index)
            clients.remove(client)
            client.close()
            break

def receive(e, N, private_key, server, public_keys, clients):                                                          #mehrere Clients empfangen
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
        thread = threading.Thread(target=handle, args=(client, private_key, N, public_keys, clients))
        thread.start()


def create_keys():
    print("RSA Start")

    p = make_prime(random.randint(1e150, 1e151))
    q = make_prime(random.randint(1e150, 1e151))
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
    return (e, N, private_key)

def main(loading_animation_thread):
    print("Hallo")
    e, N, private_key = create_keys()

    ip_tester = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ip_tester.connect(("8.8.8.8", 80))
    host = ip_tester.getsockname()[0]                                                 #LocalHost
    port = 50000                                                             #Port wählen

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)              #socket initialisieren
    server.bind((host, port))                                               #binding host und port zu einem socket
    server.listen()

    clients = []
    public_keys = []
    nicknames = ["WDQAD"]
    nicknames[0] = "ewqdq"
    print("RSA_FINISHED")
    loading_animation_thread.stop()
    label['text'] = "Server wurde gestartet!"
    receive(e, N, private_key, server, public_keys, clients)

class Loading_Animation(Stoppable_thread):
    def run(self):
        i = 0
        while not self.stopped():
            label['text'] = ''.join(["Server wird gestartet "] + ["." for _ in range(i)])
            i = (i+1)%4
            time.sleep(1)

if __name__ == "__main__":
    window = tk.Tk()
    window.geometry("500x500")
    window.title("RSA SECURED PYTHON SERVER")
    window.iconbitmap("logo_server.ico")
    label = tk.Label(window, text="Server wird gestartet ")
    label.pack()
    label.place(x=250, y=150, anchor="center")
    label['font'] = ("Courier", 20)
    
    loading_animation_thread = Loading_Animation()
    loading_animation_thread.start()

    logic = threading.Thread(target=main, args=[loading_animation_thread])
    logic.start()

    window.mainloop()

    
