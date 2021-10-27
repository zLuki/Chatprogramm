import random
import socket
import socket, threading
import json
import numpy
import re
import tkinter as tk
from tkinter import *
import time
from stoppable_thread import Stoppable_thread
from PIL import ImageTk, Image

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

def broadcast(message, public_keys, clients, nicknames):                                                 #broadcast funktion
    ascii = [ord(x) for x in message]
    for i in range(len(clients)):
        nickname = [ord(x) for x in nicknames[i]+": "]
        encrypted = [modulares_potenzieren(x, int(public_keys[i][0]), int(public_keys[i][1])) for x in nickname+ascii]
        base36_nums = [numpy.base_repr(x, base=36) for x in encrypted]
        clients[i].send((json.dumps(base36_nums)+"\r\n").encode())

def decrypt(d, text, N): #decrypt text with d
    text = json.loads(text)
    nums = [int(x, 36) for x in text]
    decrypted = [modulares_potenzieren(x, d, N) for x in nums]
    text = ''.join([chr(x) for x in decrypted])
    return text

def handle(client, private_key, N, public_keys, clients, nicknames, amount_messages):
    while True:
        index = clients.index(client)
        try:                                                            #recieving messages vom Client
            text = client.recv(int(1e6)).decode('utf8')
            print("Client "+str(clients.index(client)) + ": " +decrypt(private_key, text, N))
            broadcast(decrypt(private_key, text, N), public_keys, clients, nicknames)
            amount_messages[index] += 1
            refresh_menu(nicknames, clients, amount_messages)
        except:
            print("Client " + str(index) + " disconnected.")                                                    #löschen der Clients
            public_keys.pop(index)
            nicknames.pop(index)
            amount_messages.pop(index)
            clients.remove(client)
            client.close()
            refresh_menu(nicknames, clients, amount_messages)
            break

def receive(e, N, private_key, server, public_keys, clients, nicknames, amount_messages):                                                          #mehrere Clients empfangen
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

        nickname_client = decrypt(private_key, client.recv(int(1e6)).decode('utf8'), N)
        nicknames.append(nickname_client)

        amount_messages.append(0)

        thread = threading.Thread(target=handle, args=(client, private_key, N, public_keys, clients, nicknames, amount_messages))
        thread.start()
        refresh_menu(nicknames, clients, amount_messages)


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

def show_menu():
    connected_users['text'] = "Verbundene Benutzer:\n\n"
    connected_users_ip['text'] = "IP Adressen:\n\n"
    connected_users_send_messages['text'] = "Gesendete Nachrichten:\n\n"

def show_correct_start(host):
    global label, picture
    label['text'] = "Server wurde gestartet!\n" + host
    picture.configure(image=ImageTk.PhotoImage(Image.open("check.png").resize((150, 150))))
    time.sleep(2)
    label.destroy()
    picture.destroy()
    host_label['text'] = "HOST: "+host
    show_menu()

def refresh_menu(nicknames, clients, amount_messages):
    show_menu()
    for i in range(len(nicknames)):
        connected_users['text'] += nicknames[i] + "\n"
        connected_users_ip['text'] += clients[i].getpeername()[0] + "\n"
        connected_users_send_messages['text'] += str(amount_messages[i]) + "\n"


def main(loading_animation_thread):
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
    nicknames = []
    amount_messages = []
    print("RSA_FINISHED")
    loading_animation_thread.stop()
    show_correct_start(host)
    #label['text'] = "Server wurde gestartet!"
    receive(e, N, private_key, server, public_keys, clients, nicknames, amount_messages)

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

    picture = tk.Label(window)
    picture.pack()
    picture.place(x=250, y=300, anchor="center")

    host_label = tk.Label(window)
    host_label.pack()
    host_label.place(x=150, y=70, anchor="center")
    host_label['font'] = ("Courier", 20)

    connected_users = tk.Label(window,)
    connected_users.pack()
    connected_users.place(x=70, y=150, anchor="center")

    connected_users_ip = tk.Label(window)
    connected_users_ip.pack()
    connected_users_ip.place(x=200, y=150, anchor="center")

    connected_users_send_messages = tk.Label(window)
    connected_users_send_messages.pack()
    connected_users_send_messages.place(x=320, y=150, anchor="center")

    logic = threading.Thread(target=main, args=[loading_animation_thread])
    logic.start()

    window.mainloop()

    
