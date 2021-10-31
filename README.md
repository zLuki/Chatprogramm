# Chatprogramm

## Overview
- Server in Python
- Client in Python und Java
- Übertragung ist durch RSA verschlüsselt

## Verschlüsselung
Die Verschlüsselung funktioniert mit dem RSA Algorithmus, den wir in der Schule kennen gelernt haben. Dabei ist es wichtig, dass die Primzahlen so groß wie möglich sind.
In Python sind die Primzahlen 100 Stellen lang, in Java ungefähr 70.
Bei so großen Zahlen ist eine Primfaktorzerlegung oder eine Primzahlüberprüfung mit determinativen Algorithemn nicht mehr möglich. Deshalb benutzen wir den heuristischen Miller Rabin Algorithmus, der auch bei extrem großen Zahlen einen Primtest durchführen kann. Das Ergebnis ist jedoch zu 25% falsch, deshalb wird der Test öfters durchgeführt, um die Fehlerwahrscheinlichkeit zu verringern. Bei 12 Durchführungen ist es bereits wahrscheinlicher im Lotto zu gewinnen, als dass ein Fehler auftritt.
Um die Sicherheit der Verschlüsselung zu testen, haben wir rsa.cracker.py erstellt, der versucht den RSA zu knacken.

## Verarbeitung großer Zahlen
Python bietet bereits von Haus das Rechnen mit extrem großen Zahlen an und hat keine Grenze, wie z.B. Java mit Long.MAX_VALUE.
In Java benutzen wir die java.math.BigInteger library, um mit großen Zahlen zu rechnen.
Beim Ver- und Entschlüsseln braucht es immer wieder die Formel c^e mod N. Diese Rechnung dauert sehr lange, deshalb haben wir das modulare Potenzieren implementiert.

## Client - Server Verbindung
Es können sich beliebig viele Clients auf den Server verbinden und wieder trennen, jeder Client hat einen Nickname. Auf dem Server wird eine Statistik von verbunden Clients angezeigt.
Übertragen wird verschlüsselt, dabei entstehen sehr große Zahlen. Diese werden in Base36 konvertiert, um sie ein gutes Stück kürzer zu machen. Man kann nur Strings übertragen und keine Datenstrukturen wie Arrays, deshalb wird im stringified JSON-Format übertragen.
Es ist auch möglich mehrere Server miteinander zu verbinden, dabei ist aber aufzupassen, dass man sich nicht öfters mit dem selben Server verbindet, ansonsten gibt es Endlosschleifen im Netzwerk. (Server-Server ist nicht besonders gut getestet, da wir Zuhause nicht genug Geräte zur Verfügung hatten, und die VPN zum SNLabor nicht funktioniert hat 😒)

## Installation

### Einfach
- Output Ordner
- Den Client oder Server Ordner herunterladen
- (möglicherweise Antivirus deaktivieren)
- Die .exe Datei ausführen

### Komplizierter
Das ganze Projekt downloaden.

#### Python server und client
- Aktuelle Python3 version erforderlich.
- In CMD python server_rsa_grafic.py oder client_rsa_grafic.py eingeben.
- Eventuell module mit pip install installieren. Z.B. Tkinter und numpy, da das keine standard Module sind.

#### Java client
- Aktuelle Java version, IntelliJ und JavaFX erforderlich.
- In IntelliJ new Project from Existing Source und den client_java_grafic Ordner auswählen.
- File -> Project Structure -> Libraries -> Add -> /path/to/javaFX/lib
- main Methode in Launcher.java ausführen, mit VM Options:
```
--module-path "/path/to/javafx/lib" --add-modules javafx.controls,javafx.media,javafx.fxml
```

## Verbesserungsmöglichkeiten in Zukunft
### Objektorientierung in Python einführen:
Das Projekt hat klein gestartet und deshalb auch noch nicht objektorientiert. Es ist aber immer größer und komplizierter geworden und jetzt würde es sich definitiv lohen die Python scripts objektorientiert zu schreiben. Vor allem weil man sich dann viele globale Variablen und Übergabeparamter sparen könnte.

### Ende zu Ende Verschlüsselung
Momentan wird die Nachricht verschlüsselt an den Server geschickt, dort entschlüsselt und dann wieder verschlüsselt an den Client geschickt. Dabei hätte ein korrupter Mitarbeiter beim Server die Möglichkeit die Nachricht von Fremden mitzulesen. Man könnte in Zukunft auch Ende-zu-Ende Verschlüsselung umsteigen. Dabei dient der Server nur noch zum Schlüssel austauschen und die Nachricht kann wirklich nur von den Clients gelesen werden.


Lukas Schatzer
Philipp Olivotto