import random
import socket
import json
import threading
from tkinter import font
import numpy
import tkinter as tk
import re
import time
from stoppable_thread import Stoppable_thread

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
    print(text)
    text = json.loads(text)
    nums = [int(x, 36) for x in text]
    decrypted = [modulares_potenzieren(x, d, N) for x in nums]
    text = ''.join([chr(x) for x in decrypted])
    return text

def handle(private_key, N, server):
    while True:
        #try:
        text = server.recv(int(1e8)).decode('utf8')
        message = decrypt(private_key, text, N)
        print("Got message from Server: "+message)
        messages_label['text'] += message + "\n"
        #except:
            #print("FEHLER!")
            #server.close()
            #break

def create_keys():
    print("RSA Start")

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
    print("RSA ENDE")
    return (e, N, private_key)

def send_message():
    data = enter_message_input.get()
    ascii = [ord(x) for x in data]
    encrypted = [modulares_potenzieren(x, e, N_server) for x in ascii]
    base36_nums = [numpy.base_repr(x, 36) for x in encrypted]  
    s.send(json.dumps(base36_nums).encode())
    enter_message_input.delete(0, 'end')

def change_scene():
    window.configure(background="black")
    nickname_label.destroy()
    nickname_input.destroy()
    ip_label.destroy()
    ip_input.destroy()
    confirm_button.destroy()
    error_message_label.destroy()
    messages_label.place(x=10, y=10)
    enter_message_input.place(x=10, y=640)
    send_message_button.place(x=350, y=630)

def main(loading_animation):
    error_message_label['text'] = ""
    global s, e, N_server
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ip = ip_input.get()
    data = nickname_input.get()
    if len(data) <= 0:
        error_message_label['text'] = "Es wurde kein Nickname eingegeben!"
        loading_animation.stop()
        confirm_button['text'] = "Verbinden!"
        return
    if not re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', ip):
        error_message_label['text'] = "Die eingegebene IP Adresse ist ungültig!"
        loading_animation.stop()
        confirm_button['text'] = "Verbinden!"
        return
    try:
        s.connect((ip, 50000))
    except OSError:
        error_message_label['text'] = "Der Server "+ip+" ist nicht erreichbar!"
        loading_animation.stop()
        confirm_button['text'] = "Verbinden!"
        return

    e, N, private_key = create_keys()

    print(e)
    print(N)
    print(private_key)

    s.send((str(e)+"\r\n").encode())
    s.send((str(N)+"\r\n").encode())

    e = int(s.recv(1024).decode())
    N_server = int(s.recv(1024).decode())

    ascii = [ord(x) for x in data]
    encrypted = [modulares_potenzieren(x, e, N_server) for x in ascii]
    base36_nums = [numpy.base_repr(x, 36) for x in encrypted]  
    s.send(json.dumps(base36_nums).encode())

    thread = threading.Thread(target=handle, args=(private_key, N, s))
    thread.start()
    loading_animation.stop()
    change_scene()

class Loading_Animation(Stoppable_thread):
    def run(self):
        i = 0
        while not self.stopped():
            confirm_button['text'] = ''.join(["Generiere Schlüssel "] + ["." for _ in range(i)])
            i = (i+1)%4
            time.sleep(1)

def confirm():
    loading_animation = Loading_Animation()
    loading_animation.start()
    thread = threading.Thread(target=main, args=[loading_animation])
    thread.start()
    

if __name__ == "__main__":

    # SERVER SOCKET AND KEYS
    s = None
    e = None
    N_server = None

    window = tk.Tk()
    window.geometry("500x700")
    window.title("Chatprogramm Python Client")
    window.iconbitmap("logo_server.ico")

    # Nickname label
    nickname_label = tk.Label(window, text="Nickname:")
    nickname_label.place(x=100, y=200)
    nickname_label['font'] = ("Courier", 13)
    # IP label
    ip_label = tk.Label(window, text="IP Adresse:")
    ip_label.place(x=100, y=250)
    ip_label['font'] = ("Courier", 13)
    # Nickname input
    nickname_input = tk.Entry(window)
    nickname_input.place(x=250, y=200)
    nickname_input['font'] = ("Courier", 13)
    # IP input
    ip_input = tk.Entry(window)
    ip_input.place(x=250, y=250)
    ip_input['font'] = ("Courier", 13)
    # confirm button
    confirm_button = tk.Button(window, text="Verbinden!", command=lambda:confirm())
    confirm_button.place(x=100, y=300)
    confirm_button['font'] = ("Courier", 18)
    # error message
    error_message_label = tk.Label(window)
    error_message_label['font'] = ("Courier", 13)
    error_message_label.place(x=10, y=350)
    error_message_label.configure(fg="red")

    # Messages box
    messages_label = tk.Label(window, width=30, height=20, anchor="n")
    messages_label.configure(background="black")
    messages_label['font'] = ("Courier", 20)
    messages_label.configure(fg="white")
    # Enter Message box
    enter_message_input = tk.Entry(window, borderwidth=5, relief="solid", highlightbackground="white", highlightcolor="white", highlightthickness=3, bd=0, insertbackground="white")
    enter_message_input['font'] = ("Courier", 20)
    enter_message_input.configure(background="black")
    enter_message_input.configure(fg="white")
    # Send message button
    send_message_button = tk.Button(window, text="Senden", command=lambda:send_message())
    send_message_button['font'] = ("Courier", 20)
    

    window.mainloop()
