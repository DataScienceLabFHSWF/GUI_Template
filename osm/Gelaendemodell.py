#!/usr/bin/env python3

import os
import sys
import webbrowser
import struct
from tkinter import Tk
from tkinter.filedialog import askdirectory
from math import sqrt, sin, cos, tan, radians, degrees, floor

print("""
Dieses Python3-Skript erstellt Höhenmodelle für CAD und 3D-Druck.

Mit zwei Dezimalgradkoordinaten geben Sie die Eckpunkte einer rechteckigen
Geländeoberfläche an, für die dieses Programm diverse 3D-Dateien erzeugt:

 - ein Höhenmodell im STL-Format für 3D-Drucker,
 - eine DXF-Datei mit 3D-Flächen, die in Regionen umgewandelt und zu einem
   Volumenmodell geheftet werden können,
 - eine auf die Auswahl reduzierte XYZ-Datei und
 - diverse AutoCAD- bzw. BricsCAD-Befehlsskripte (SCR).
""")

# Die CAD-Skripte enthalten Befehle zur Erzeugung von Prismenfeldern aus
# 3D-Körpern, sodass Volumenbefehle angewendet werden können, sowie Befehle
# zur Erzeugung von verschiedenen Oberflächenmodellen.

# Das aus Drei- und Vierecken zusammengesetzte Oberflächenmodell ist im
# Ergebnis mit dem Inhalt der DXF-Datei identisch und lässt sich durch
# Anwendung der beiden Befehle "Region" und "Heften" ebenfalls in ein
# Volumenmodell umwandeln.

# Das Programm wurde für die öffentlichen Höhendaten für digitale
# Geländemodelle in NRW geschrieben, lässt sich aber mit geringen Anpassungen
# auch für andere DGM-Daten nutzen.

# Datenquelle:
# http://www.bezreg-koeln.nrw.de/
#        brk_internet/geobasis/hoehenmodelle/gelaendemodelle/
# bzw. https://www.opengeodata.nrw.de/produkte/

# Autor: Dipl.-Ing. Martin Vogel, Hochschule Bochum, 2017, 2018

# Lizenz: Namensnennung - Weitergabe unter gleichen Bedingungen 3.0 Deutschland
# (CC BY-SA 3.0 DE) https://creativecommons.org/licenses/by-sa/3.0/de/

# Version 12 vom 3. Juni 2018
#   Anzeige und PDF-Export eines Höhendiagramms mittels Matplotlib.

# Version 11 vom 18. Juni 2017
#   Zu fehlenden Kacheln wird nun angegeben, in welchen Ortsdateien diese
#   zu finden sind. Dazu mussten alle 396 Dateien einmal heruntergeladen und
#   diese 269 Gigabyte ZIP-Dateien katalogisiert werden. -> Gelaendekatalog.csv

# Version 10 vom 15. Juni 2017
#   UTM-Koordinatenumrechnung jetzt ohne externes Modul und nach vereinfachtem
#   Algorithmus.

# Version 9 vom 13. Juni 2017
#   DXF-Export der Dreiecks- und Vierecksflächen aus Version 8.

# Version 8 vom 11. Juni 2017
#   Oberflächenmodell für CAD-Skript aus einzelnen Dreiecksflächen, wie in der
#   STL-Datei, Seitenflächen und Boden jedoch aus Vierecken.

# Version 7 vom 9. Juni 2017
#   Jetzt mit 3D-Netz, viel schneller als Volumenkörper im CAD-Programm.
#   Leider kann BricsCAD aus dieser Oberfläche keinen Volumenkörper heften.

# Version 6 vom 21. März 2017
#   Jetzt mit Log-Datei zur Garantie der Wiederholbarkeit.

# Version 5 vom 19. März 2017
#   Jetzt mit variabler Höhe der Unterseite. Es gibt in NRW tatsächlich Flächen,
#   die weit unterhalb des Meeresspiegels liegen. (Tagebau Etzweiler: -298,90m!)

# Version 4 vom 18. März 2017
#   Jetzt mit binärem STL-Export. Die Dateien sind nur noch halb so groß
#   und werden viel schneller gelesen als ASCII-STL-Dateien.

# Version 3 vom 17. März 2017
#   Einige mögliche Fehleingaben werden jetzt freundlich abgefangen.
#   Erweiterung um CAD-Skript für Dreiecksprismen, um den Minecraft-Effekt
#   loszuwerden.

# Version 2 vom 16. März 2017
#   Jetzt mit Eingabe der Höhenauflösung.
#   Außerdem werden nicht mehr alle gefundenen Punkte im Dictionary
#   abgelegt, sondern nur noch die später auch benötigten.

# Ideen für Erweiterungen:
#  - Grafische Oberfläche (mit Kontrolle der Kachelabdeckung) einbauen.
#  - Automatisches Nachladen fehlender Kacheln.
#  - In der DXF-Datei noch Werte für Zoom, Blickwinkel, Geokoordinaten,
#    Einheit Meter usw. eintragen.
#  - Klären, warum FreeCAD nur eine einzige 3D-Fläche der DXF-Datei darstellt.

# Aufräumen:
#  - Alte C-Formatstrings durch f-Strings ersetzen.

def sysexit():
    input("\nProgramm wird beendet. [Enter]")
    sys.exit()

def log(s, sichtbar=True):
    "Bildschirmmeldung mit Protokollierung"
    with open(name+".log","a") as logfile:
        logfile.write(f"{s}\n")
    if sichtbar:
        print(f"\n{s}")

def utm(Bg,Lg):
    "Umrechnung von Breitengrad und Längengrad in UTM-Koordinaten"
    # http://www.ottmarlabonde.de/L1/UTMBeispielRechnung.htm
    # Literatur: A. Schödlbauer,
    #     Rechenformeln und Rechenbeispiele zur Landesvermessung,
    #     Teil 2, Herbert WichmannVerlag Karlsruhe

    L = radians(Lg)
    B = radians(Bg)
    tB = tan(B)
    cB = cos(B)

    # Halbachsen des WGS84-Ellipsoids:
    # a = 6378137.0
    # b = 6356752.314

    # Radiusreduzierung
    mH = 0.9996

    # c = a**2/b
    c = 6399593.626005325

    # eq = (a**2-b**2)/b**2
    eq = 0.006739496819936062

    # E0 = c*(1-3/4*eq+45/64*eq**2-175/256*eq**3+11025/16384*eq**4)
    E0 = 6367449.145759811

    # E2 = c*(-3/8*eq+15/32*eq**2-525/1024*eq**3+2205/4096*eq**4)
    E2 = -16038.508797800609

    # E4 = c*(15/256*eq**2-105/1024*eq**3+2205/16384*eq**4)
    E4 = 16.83262765753934
    
    # E6 = c*(-35/3072*eq**3+315/12288*eq**4)
    E6 = -0.021980907677118407

    LL = E0*B + E2*sin(2*B) + E4*sin(4*B) + E6*sin(6*B)
    x0 = mH*LL

    LhL = 3 + 6*floor(degrees(L)/6)
    Zone = 30 + (3+LhL)/6

    DL = L - radians(LhL)

    etaq = eq*cB**2
    Nq = c/sqrt(1+etaq)

    x2 = mH/2*Nq*tB*cB**2
    x4 = mH/24*Nq*tB*cB**4*(5-tB**2+9*etaq)
    x6 = mH/720*Nq*tB*cB**6*(61-58*tB**2+tB**4)

    N = x0 + x2*DL**2 + x4*DL**4 + x6*DL**6

    y1 = mH*Nq*cB
    y3 = mH/6*Nq*cB**3*(1-tB**2+etaq)
    y5 = mH/120*Nq*cB**5*(5-18*tB**2+tB**4+etaq*(14-58*tB**2))

    E = y1*DL + y3*DL**3 + y5*DL**5 + 500000

    return N, E, Zone


# Schritt 1: Wie soll das Kind heißen?
print("\nGeben Sie einen Basisnamen für die erzeugten Dateien an!\n"
      "Existierende Dateien mit diesem Namen und den Endungen .dxf, .scr,\n"
      ".xyz, .pdf und .stl werden ohne Warnung überschrieben.\n")

name = input("Dateiname ohne Endung: ")
log("Basisname: "+name, sichtbar=False)

# Schritt 2: Wo sind die Geodaten?
print("Bitte wählen Sie den Ordner mit den ausgepackten XYZ-Dateien aus:")
# Für den Dialog müssen wir Tk laden.
Fenster = Tk()
# Wir brauchen das Hauptfenster hier nicht.
Fenster.withdraw()
# Dialogfenster
ordner = askdirectory(title="Bitte den gewünschten Ordner doppelklicken")

if not ordner:
    print("\nKein Ordner ausgewählt.")
    sysexit()
    
log(f"Gewählter Ordner: {ordner}")

# Schritt 3: Welches Gebiet wollen wir modellieren?
print("\nGeben Sie zwei gegenüberliegende Eckpunkte des zu modellierenden\n"
      "Rechtecks an! Das Eingabeformat ist (Breite, Länge) in Dezimalgrad,\n"
      "also beispielsweise 51.335757,7.479087 – Sie können die Koordinaten\n"
      "direkt aus Google Maps oder Ihrem GPS-Gerät übernehmen.\n")

try:
    lat1, lon1 = eval(input("Erstes Eckpunktkoordinatenpaar: "))
    lat2, lon2 = eval(input("Gegenüberliegendes Koordinatenpaar: "))
except:
    print("Es wurden keine zwei mit einem Komma getrennte Zahlen erkannt.")
    sysexit()
    
# Die Eingabe oben war beliebig, wir brauchen aber gleich die Südwestecke
# unten links und die Nordostecke oben rechts:
ul_lat = min(lat1, lat2)
ul_lon = min(lon1, lon2)
or_lat = max(lat1, lat2)
or_lon = max(lon1, lon2)
log(f"Geokoordinaten: {ul_lat},{ul_lon} {or_lat},{or_lon}",
    sichtbar=False)

# Umrechnung der Dezimalgradkoordinaten ins UTM-System; aus Längen- und
# Breitengrad werden ein Nordwert, ein Ostwert und eine Zonennummer.
n, e, zn = utm(ul_lat, ul_lon)

# Die Zonennummer ist in den Dateien, die unter opengeodata.nrw.de
# heruntergeladen werden können, dem Ostwert vorangestellt.
ul_e = int("%i%i"%(zn,e))

# Der Nordwert wird übernommen.
ul_n = int(n)

# Das gleiche noch einmal für die Nordostecke unseres Rechtecks.
n, e, zn = utm(or_lat, or_lon)
or_e = int("%i%i"%(zn,e))
or_n = int(n)

log("\nLage und Größe des ausgewählten Rechtecks:")
log("UTM-Koordinaten: %i,%i %i,%i in Zone %i" % (ul_e,ul_n,or_e,or_n,zn))
log("Ausdehnung Ost-West: %i m" % (or_e-ul_e))
log("Ausdehnung Nord-Süd: %i m" % (or_n-ul_n))
log("Fläche: %i m²" % ((or_e-ul_e)*(or_n-ul_n)))

# Liste der zu öffnenden XYZ-Dateien zusammenbauen:
# Bei den NRW-Höhendaten kann man am Dateinamen erkennen, ob gesuchte
# Punkte in ihnen enthalten sein könnten.
# Der Dateiname gibt die untere linke Ecke einer 2000x2000-m²-Kachel an.
# Beispiel für einen Dateinamen: dgm1_32368_5700_2_nw.xyz
# Hier sind die Ostwerte 32368000 bis 32369999 und die Nordwerte
# 5700000 bis n5701999 enthalten.

print("\nUntersuche Vollständigkeit der Höhendaten…")
xyz_Liste = []
e_min = 2 * (ul_e // 2000)
e_max = 2 * (or_e // 2000)
n_min = 2 * (ul_n // 2000)
n_max = 2 * (or_n // 2000)
for e in range(e_min,e_max+1,2):
    for n in range(n_min,n_max+1,2):
        xyz_Liste.append("dgm1_%i_%i_2_nw.xyz" % (e,n))

# Sind alle Dateien vorhanden?
fehlende_zip=[]
for xyz_Name in xyz_Liste:
    if not os.path.isfile(ordner+"/"+xyz_Name):
        print("Die XYZ-Datei %s fehlt!" % xyz_Name)
        # print("Sie finden Sie in folgenden ZIP-Archiven:")
        with open("Gelaendekatalog.csv") as csv:
            for Zeile in csv:
                if xyz_Name in Zeile[1:]:
                    zip_name = Zeile.split()[0]
                    # print(zip_name)
                    if zip_name not in fehlende_zip:
                        fehlende_zip.append(zip_name)

if fehlende_zip:
    print("\nBitte laden Sie zuerst die fehlenden ZIP-Archive herunter und\n"
          "entpacken Sie die darin enthaltenen XYZ-Dateien in den Ordner\n"
          "%s.\n" % ordner)
    print("In diesen Archiven können Sie die fehlenden Kacheln finden:\n")
    print("\n".join(fehlende_zip))
    print("\nDie Downloadseite\n"
          "https://www.opengeodata.nrw.de/produkte/geobasis/dgm/dgm1/\n"
          "wird nun im Webbrowser aufgerufen …")
    webbrowser.open("https://www.opengeodata.nrw.de/"
                    "produkte/geobasis/dgm/dgm1/")
    sysexit()

print("… alle benötigten Dateien sind vorhanden.")
        
# Alle Dateien sind vorhanden, jetzt kümmern wir uns um die Modelldetails:
print("\nDie horizontale Auflösung der Daten beträgt einen Meter, was bei\n"
      "größeren Flächen zu extremen Dateigrößen und Verarbeitungszeiten der\n"
      "erzeugten Modelle führen kann. Tipp: beginnen Sie mit ungefähr 1000\n"
      "Punkten auf der gesamten Fläche und erhöhen Sie die Auflösung in\n"
      "weiteren Durchläufen schrittweise.\n")

# Vorschlag für die horizontale Auflösung ermitteln
kl0 = max(1,int(((or_e-ul_e)*(or_n-ul_n)/1000)**0.5))
p0 = ((or_e-ul_e)//kl0) * ((or_n-ul_n)//kl0)
print("Bei %i m Auflösung würden Sie beispielsweise %i Punkte erhalten.\n" % (
    kl0, p0))

try:
    kl = int(input("Geben Sie einen ganzzahligen Wert ein [m]: "))
except:
    kl = 1

print("\nDie vertikale Auflösung der Daten beträgt einen Zentimeter. Das ist\n"
      "normalerweise in Ordnung. Für einen Höhenschichteneffekt wie bei\n"
      "architektonischen Geländemodellen kann dieser Wert auch auf 100 oder\n"
      "mehr geändert werden, je nach gewünschter Effektstärke.\n"
      "Nebeneffekt: Das CAD-Volumenmodell benötigt bei größeren Werten\n"
      "deutlich weniger Speicherplatz.\n")

try:
    kh = int(input("Geben Sie einen ganzzahligen Wert ein [cm]: "))
except:
    kh = 1

xmax = or_e - (or_e-ul_e) % kl
ymax = or_n - (or_n-ul_n) % kl

log("Horizontale Auflösung [m]: %i" % kl, sichtbar=False)
log("Vertikale Auflösung [cm]: %i" % kh, sichtbar=False)
log("\nAbstand der neuen Punkte: %i m" % kl)
log("\nAusdehnung Ost-West: %i m" % (xmax-ul_e))
log("Ausdehnung Nord-Süd: %i m" % (ymax-ul_n))
fqm = (xmax-ul_e)*(ymax-ul_n)
log("Fläche: %i m² bzw. %.3f km²" % (fqm,fqm/1e6))

# Alle gefundenen Höhenwerte werden zunächst in ein Dictionary
# geschrieben, aus dem sie für die einzelnen Dateien wieder
# ausgelesen werden.

D = {}

# Die Höhe der Unterseite ist nicht null, sondern orientiert sich
# am tatsächlichen Gelände.

minh = float("inf")
maxh = -float("inf")

# Schleife über alle zu verwendenden Eingabedateien
for dateiname in xyz_Liste:
    with open(ordner+"/"+dateiname) as dgm:
        log("Verwende XYZ-Datei %s" % dateiname)
        for zeile in dgm:
            # Beispiel für eine Zeile aus Bochum:
            # 32372000.00 5706000.00   61.32
            try:
                x,y,h = zeile.split()
                x = int(float(x))
                y = int(float(y))
                h = float(h)
            except ValueError:
                print("Abbruch, falsches Format:",zeile)
                break
            # Koordinaten der Zeile im gesuchten Rechteck?
            if ul_e <= x <= or_e and ul_n <= y <= or_n:
                # Liegt der Punkt im ausgedünnten Horizontalraster?
                if not (x - ul_e) % kl and not (y - ul_n) % kl:
                    # Punkt wird bei gewählter Auflösung verwendet
                    if kh != 1:
                        # Höhenwerte werden gerundet
                        h = round(round(h*100/kh)*kh/100, 2)
                    D[x,y] = h
                    minh = min(h, minh)
                    maxh = max(h, maxh)

log(f"Größte gefundene Höhe: {maxh:.2f} Meter")
log(f"Kleinste gefundene Höhe: {minh:.2f} Meter")
minhs = minh # "echten" minh-Wert merken
# Unterkante des Modells absenken:
minh = 10 * floor(minh/10) - 10
log(f"Setze Unterkante auf {minh:.2f} Meter.")
log(f"Neue Modellhöhe: {maxh-minh:.2f} Meter") 

# Diagramm anzeigen
print("\nHöhendiagramm wird erzeugt.")
try:
    import matplotlib.pyplot as plt

    # Keine Interaktion, Diagramm nur anzeigen …
    plt.rcParams['toolbar'] = 'None'
    # Einheitlicher Maßstab für x und y
    plt.axis('equal')

    # Für das Diagramm wird die untere linke Ecke auf (0,0)
    # gesetzt. Wer kann schon was mit UTM-Koordinaten anfangen?
    
    # Liste der x-Werte
    xi = list(range(0,or_e-ul_e+1,kl))
    # Liste der y-Werte
    yi = list(range(0,or_n-ul_n+1,kl))
    # Matrix der Höhenwerte für alle x-y-Paare
    zi = [[D[(x+ul_e,y+ul_n)] for x in xi] for y in yi]

    # Anzahl der Höhenlinien: etwa 10 (7 bis 14)
    nh = (maxh-minhs) * 100
    while nh > 70: nh = int(nh/10)
    if nh > 35: nh = int(nh/5)
    if nh > 14: nh = int(nh/2)
    # print("Zeichne",nh,"Höhenlinien.")

    # Höhenlinien
    plt.contour(xi, yi, zi, nh, linewidths=1, colors="k")
    # farbige Oberfläche
    plt.pcolormesh(xi, yi, zi, cmap = plt.get_cmap('terrain'))
    # Legende
    plt.colorbar()
    # Überschrift
    plt.title(f"Ausschnittgröße {xmax-ul_e}×{ymax-ul_n} m\n"
              f"(0,0) bei {ul_lat}° Nord, {ul_lon}° Ost")
    plt.gcf().canvas.set_window_title(f'Höhendiagramm {name}')
    # anzeigen und zurück zum Programm …
    plt.show(block=False)
    # Bild als PDF speichern
    ausname = name+".pdf"
    log("Schreibe PDF-Ausgabedatei: %s" % ausname)
    plt.savefig(ausname, bbox_inches='tight')
    
except:
    print("\nFehler: Diagramm kann nicht angezeigt werden."
          " Ist matplotlib nicht installiert?\n")
    plt=None

# Alle Punkte als simple XYZ-Datei sichern

ausname = name+".xyz"
log("Schreibe XYZ-Ausgabedatei: %s" % ausname)

with open(ausname,"w") as aus:
    for x in range(ul_e,or_e+1,kl):
        for y in range(ul_n,or_n+1,kl):
            aus.write("%i %i %.2f\n"%(x,y,D[(x,y)]))

# DXF-Export

ausname = name+".dxf"
log("Schreibe DXF-Datei mit 3D-Flächen: %s" % ausname)

# Weil 3D-Solids in einem obskuren „Geheimformat“ gespeichert werden, wird
# hier nur die umhüllende Fläche erzeugt. Diese muss im CAD-Programm mittels
# der Befehle REGION und HEFTEN in einen SOLID umgewandelt werden, um einen
# richtigen Geländekörper zu erhalten.

with open(ausname,"w") as aus:
    aus.write("0\nSECTION\n2\nHEADER\n"
              "9\n$ACADVER\n1\nAC1006\n"
              "9\n$INSBASE\n10\n0.0\n20\n0.0\n30\n0.0\n"
              "9\n$INSUNITS\n70\n6\n"
              "9\n$EXTMIN\n10\n0.0\n20\n0.0\n"
              "9\n$EXTMAX\n10\n%f\n20\n%f\n" % (xmax-ul_e, ymax-ul_n) +
              "9\n$LIMMIN\n10\n0.0\n20\n0.0\n"
              "9\n$LIMMAX\n10\n%f\n20\n%f\n" % (xmax-ul_e, ymax-ul_n) +
              "0\nENDSEC\n"
              "0\nSECTION\n2\nENTITIES\n")
    
    # Geländeoberfläche
    for x in range(ul_e,xmax+1-kl,kl):
      xu = x - ul_e
      for y in range(ul_n,ymax+1-kl,kl):
        yu = y - ul_n
        h1 = D[x,y]
        h2 = D[x+kl,y]
        h3 = D[x,y+kl]
        h4 = D[x+kl,y+kl]
        aus.write("0\n3DFACE\n"
                  "10\n%i\n20\n%i\n30\n%s\n"%(xu, yu, h1) +
                  "11\n%i\n21\n%i\n31\n%s\n"%(xu+kl, yu+kl, h4) +
                  "12\n%i\n22\n%i\n32\n%s\n"%(xu+kl, yu, h2) +
                  "13\n%i\n23\n%i\n33\n%s\n"%(xu+kl, yu, h2))
        aus.write("0\n3DFACE\n"
                  "10\n%i\n20\n%i\n30\n%s\n"%(xu, yu, h1) +
                  "11\n%i\n21\n%i\n31\n%s\n"%(xu, yu+kl, h3) +
                  "12\n%i\n22\n%i\n32\n%s\n"%(xu+kl, yu+kl, h4) +
                  "13\n%i\n23\n%i\n33\n%s\n"%(xu+kl, yu+kl, h4))

      
    # Unterseite
    aus.write("0\n3DFACE\n"
              "10\n%i\n20\n%i\n30\n%.2f\n"%(0,0, minh) +
              "11\n%i\n21\n%i\n31\n%.2f\n"%(xmax-ul_e, 0, minh) +
              "12\n%i\n22\n%i\n32\n%.2f\n"%(xmax-ul_e, ymax-ul_n, minh) +
              "13\n%i\n23\n%i\n33\n%.2f\n"%(0, ymax-ul_n, minh))
        
    # Linke Wand
    for y in range(ul_n,ymax+1-kl,kl):
        yu = y-ul_n
        h1 = D[ul_e,y]
        h2 = D[ul_e,y+kl]
        aus.write("0\n3DFACE\n"
                  "10\n0\n20\n%i\n30\n%.2f\n"%(yu, minh) +
                  "11\n0\n21\n%i\n31\n%.2f\n"%(yu+kl, minh) +
                  "12\n0\n22\n%i\n32\n%.2f\n"%(yu+kl, h2) +
                  "13\n0\n23\n%i\n33\n%.2f\n"%(yu, h1))
        
    # Rechte Wand
    for y in range(ul_n,ymax+1-kl,kl):
        xu = xmax-ul_e
        yu = y-ul_n
        h1 = D[xmax,y]
        h2 = D[xmax,y+kl]
        aus.write("0\n3DFACE\n"
                  "10\n%i\n20\n%i\n30\n%.2f\n" % (xu, yu, minh) +
                  "11\n%i\n21\n%i\n31\n%.2f\n" % (xu, yu, h1) +
                  "12\n%i\n22\n%i\n32\n%.2f\n" % (xu, yu+kl, h2) +
                  "13\n%i\n23\n%i\n33\n%.2f\n" % (xu, yu+kl, minh))
        
    # Vordere Wand
    for x in range(ul_e,xmax+1-kl,kl):
        h1 = D[x,ul_n]
        h2 = D[x+kl,ul_n]
        xu = x - ul_e
        aus.write("0\n3DFACE\n"
                  "10\n%i\n20\n0\n30\n%.2f\n" % (xu, minh) +
                  "11\n%i\n21\n0\n31\n%.2f\n" % (xu, h1) +
                  "12\n%i\n22\n0\n32\n%.2f\n" % (xu+kl, h2) +
                  "13\n%i\n23\n0\n33\n%.2f\n" % (xu+kl, minh))
        
    # Hintere Wand
    for x in range(ul_e,xmax+1-kl,kl):
        xu = x - ul_e
        yu = ymax - ul_n
        h1 = D[x,ymax]
        h2 = D[x+kl,ymax]
        aus.write("0\n3DFACE\n"
                  "10\n%i\n20\n%i\n30\n%.2f\n"%(xu, yu, minh) +
                  "11\n%i\n21\n%i\n31\n%.2f\n"%(xu+kl, yu, minh) +
                  "12\n%i\n22\n%i\n32\n%.2f\n"%(xu+kl, yu, h2) +
                  "13\n%i\n23\n%i\n33\n%.2f\n"%(xu, yu, h1))
        
    aus.write("0\nENDSEC\n0\nEOF\n")
            


# Diverse Skripte für AutoCAD/BricsCAD

def scr_intro():
    "Nimmt Grundeinstellungen des Zeichnungseditors vor"
    # Rückgängigmachen ausschalten
    # Koordinateneingabe hat Vorrang vor Objektfang,
    # Einheit Meter,
    # Ansicht schräg von Südwesten,
    # Visueller Stil Drahtmodell (Geschwindigkeit!),
    # Zoom auf interessanten Quader
    return ("Zurück S K\n"
            "OSnapCoord 1\n"
            "_InsUnits 6\n"
            "APunkt -1,-2,2\n"
            "-Vis A Drahtmodell\n"
            "Zoom F 0,0,%f %i,%i,%f\n" % (minh, or_e-ul_e, or_n-ul_n, maxh))

# Einstellungen nach Skriptende:
def scr_exit():
    # Rückgängigmachen einschalten
    # Zoom auf Grenzen
    return ("Zurück A\n"
            "Zoom G\n")


ausname = name+".quadratprismen.scr"
log("Schreibe CAD-Skriptdatei mit Quadratprismenfeld: %s " % ausname)

# Eigentlich wäre es universeller, anstelle der deutschsprachigen
# Bezeichner englischsprachige Bezeichner mit vorangestelltem Unterstrich
# zu verwenden. Dummerweise kommt BricsCAD damit nicht immer zurecht.
with open(ausname,"w") as aus:
    aus.write(scr_intro())

    for x in range(ul_e,or_e+1,kl):
        for y in range(ul_n,or_n+1,kl):
            aus.write("Quader %i,%i,%.2f %i,%i,%.2f\n" % (
                x-ul_e, y-ul_n, minh,
                x-ul_e+kl, y-ul_n+kl, D[(x,y)]))
            
    aus.write(scr_exit())

ausname = name+".dreiecksprismen.scr"
log("Schreibe CAD-Skriptdatei mit Dreiecksprismenfeld: %s" % ausname)

with open(ausname,"w") as aus:
    aus.write(scr_intro())
    
    for x in range(ul_e,xmax+1-kl,kl):
        for y in range(ul_n,ymax+1-kl,kl):
            h1 = float(D[x,y])
            x1, y1 = x-ul_e, y-ul_n
            h2 = float(D[x+kl,y])
            x2, y2 = x1+kl, y1
            h3 = float(D[x+kl,y+kl])
            x3, y3 = x2, y1+kl
            h4 = float(D[x,y+kl])
            x4, y4 = x1, y3
            hmax = max(h1, h2, h3, h4)
            # Dreieck auf Nullebene zeichnen …
            aus.write("3DPoly %i,%i,%.2f %i,%i,%.2f %i,%i,%.2f S\n" % (
                x1,y1,minh, x2,y2,minh, x3,y3,minh))
            # … bis zum höchsten Punkt hochziehen …
            aus.write("_extrude L  %f\n" % (hmax-minh))
            # … und oben schräg abschneiden.
            aus.write("Kappen L   %i,%i,%f %i,%i,%f %i,%i,%f %i,%i,%f\n" %
                      (x1,y1,h1, x2,y2,h2, x3,y3,h3, x1,y1,minh))
            # Und nochmal für das zweite Dreieck:
            aus.write("3DPoly %i,%i,%.2f %i,%i,%.2f %i,%i,%.2f S\n" % (
                x1,y1,minh, x4,y4,minh, x3,y3,minh))
            aus.write("_extrude L  %f\n" % hmax)
            aus.write("Kappen L   %i,%i,%f %i,%i,%f %i,%i,%f %i,%i,%f\n" %
                      (x1,y1,h1, x4,y4,h4, x3,y3,h3, x1,y1,minh))
            
    aus.write(scr_exit())

ausname = name+".mesh.scr"
log("Schreibe CAD-Skriptdatei mit 3D-Netz (Mesh): %s " % ausname)

# Beim Quadratnetz hat BricsCAD die Einschränkung, dass es maximal
# 256×256 Knoten haben darf. Daher muss hier ausgedünnt werden.

with open(ausname,"w") as aus:
    aus.write(scr_intro())
    n = 1
    klm = kl
    while (or_e-ul_e+1)//klm > 256 or (or_n-ul_n+1)//klm > 256:
        n += 1
        klm = kl * n
    if n>1:
        log("Verwende nur jeden %i. Punkt pro Richtung." % n)

    # Gelände
    aus.write("3dnetz %i %i\n" % ((or_e-ul_e)//klm+1,(or_n-ul_n)//klm+1))
    for x in range(ul_e,or_e+1,klm):
        for y in range(ul_n,or_n+1,klm):
            aus.write("%i,%i,%f\n" % (x-ul_e,y-ul_n,D[(x,y)]))
    # Seitenflächen
    y = ul_n
    aus.write("3dnetz %i 2\n" % ((or_e-ul_e)//klm+1))
    for x in range(ul_e,or_e+1,klm):
        aus.write("%i,%i,%f\n" % (x-ul_e,y-ul_n,minh))
        aus.write("%i,%i,%f\n" % (x-ul_e,y-ul_n,D[(x,y)]))
    y = range(ul_n,or_n+1,klm)[-1]
    aus.write("3dnetz %i 2\n" % ((or_e-ul_e)//klm+1))
    for x in range(ul_e,or_e+1,klm):
        aus.write("%i,%i,%f\n" % (x-ul_e,y-ul_n,minh))
        aus.write("%i,%i,%f\n" % (x-ul_e,y-ul_n,D[(x,y)]))
    x = ul_e            
    aus.write("3dnetz %i 2\n" % ((or_n-ul_n)//klm+1))
    for y in range(ul_n,or_n+1,klm):
        aus.write("%i,%i,%f\n" % (x-ul_e,y-ul_n,minh))
        aus.write("%i,%i,%f\n" % (x-ul_e,y-ul_n,D[(x,y)]))
    x = range(ul_e,or_e+1,klm)[-1]           
    aus.write("3dnetz %i 2\n" % ((or_n-ul_n)//klm+1))
    for y in range(ul_n,or_n+1,klm):
        aus.write("%i,%i,%f\n" % (x-ul_e,y-ul_n,minh))
        aus.write("%i,%i,%f\n" % (x-ul_e,y-ul_n,D[(x,y)]))
    # Boden
    x_max = range(ul_e,or_e+1,klm)[-1]-ul_e
    y_max = range(ul_n,or_n+1,klm)[-1]-ul_n
    aus.write("3dfläche\n")
    aus.write("0,0,%f " % (minh))
    aus.write("0,%i,%f " % (y_max, minh))
    aus.write("%i,%i,%f " % (x_max, y_max, minh))
    aus.write("%i,0,%f \n" % (x_max, minh))
            
    aus.write(scr_exit())

ausname = name+".3dflächen.scr"
log("Schreibe CAD-Scriptdatei mit 3D-Flächen: %s" % ausname)

# Das 3D-Netz oben lässt sich in BricsCAD blöderweise nicht zu einem
# Solid umformen. Hier wird daher nun derselbe Algorithmus verwendet,
# der auch für STL-Dateien zum Einsatz kommt.
# Für die Seiten und den Boden werden Vierecke verwendet.

with open(ausname,"w") as aus:
    aus.write(scr_intro())
    
    # Geländeoberfläche
    for x in range(ul_e,xmax+1-kl,kl):
      xu = x - ul_e
      for y in range(ul_n,ymax+1-kl,kl):
        yu = y - ul_n
        h1 = D[x,y]
        h2 = D[x+kl,y]
        h3 = D[x,y+kl]
        h4 = D[x+kl,y+kl]
        aus.write("3dfläche\n"
                  "%i,%i,%s\n"%(xu, yu, h1) +
                  "%i,%i,%s\n"%(xu+kl, yu+kl, h4) +
                  "%i,%i,%s\n\n\n"%(xu+kl, yu, h2))
        aus.write("3dfläche\n"
                  "%i,%i,%s\n"%(xu, yu, h1) +
                  "%i,%i,%s\n"%(xu, yu+kl, h3) +
                  "%i,%i,%s\n\n\n"%(xu+kl, yu+kl, h4))

      
    # Unterseite
    aus.write("3dfläche\n"
              "%i,%i,%.2f\n"%(0,0, minh) +
              "%i,%i,%.2f\n"%(xmax-ul_e, 0, minh) +
              "%i,%i,%.2f\n"%(xmax-ul_e, ymax-ul_n, minh) +
              "%i,%i,%.2f\n\n"%(0, ymax-ul_n, minh))
        
    # Linke Wand
    for y in range(ul_n,ymax+1-kl,kl):
        yu = y-ul_n
        h1 = D[ul_e,y]
        h2 = D[ul_e,y+kl]
        aus.write("3dfläche\n"
                  "0,%i,%.2f\n"%(yu, minh) +
                  "0,%i,%.2f\n"%(yu+kl, minh) +
                  "0,%i,%.2f\n"%(yu+kl, h2) +
                  "0,%i,%.2f\n\n"%(yu, h1))
        
    # Rechte Wand
    for y in range(ul_n,ymax+1-kl,kl):
        xu = xmax-ul_e
        yu = y-ul_n
        h1 = D[xmax,y]
        h2 = D[xmax,y+kl]
        aus.write("3dfläche\n"
                  "%i,%i,%.2f\n" % (xu, yu, minh) +
                  "%i,%i,%.2f\n" % (xu, yu, h1) +
                  "%i,%i,%.2f\n" % (xu, yu+kl, h2) +
                  "%i,%i,%.2f\n\n" % (xu, yu+kl, minh))
        
    # Vordere Wand
    for x in range(ul_e,xmax+1-kl,kl):
        h1 = D[x,ul_n]
        h2 = D[x+kl,ul_n]
        xu = x - ul_e
        aus.write("3dfläche\n"
                  "%i,0,%.2f\n" % (xu, minh) +
                  "%i,0,%.2f\n" % (xu, h1) +
                  "%i,0,%.2f\n" % (xu+kl, h2) +
                  "%i,0,%.2f\n\n" % (xu+kl, minh))
        
    # Hintere Wand
    for x in range(ul_e,xmax+1-kl,kl):
        xu = x - ul_e
        yu = ymax - ul_n
        h1 = D[x,ymax]
        h2 = D[x+kl,ymax]
        aus.write("3dfläche\n"
                  "%i,%i,%.2f\n"%(xu, yu, minh) +
                  "%i,%i,%.2f\n"%(xu+kl, yu, minh) +
                  "%i,%i,%.2f\n"%(xu+kl, yu, h2) +
                  "%i,%i,%.2f\n\n"%(xu, yu, h1))
            
    aus.write(scr_exit())

ausname = name+".ascii.stl"
log("Schreibe STL-Datei für 3D-Druck (ASCII): %s" % ausname)

# Die Flächen umhüllen einen Quader, der unten auf Höhe minh aufliegt
# und oben durch die Geländeoberfläche abgeschnitten wird.

# Für die „Flächennormalen“ wird hier immer eine der Achsenrichtungen
# eingesetzt. Für die Geländeoberfläche ist das beispielsweise die
# nach oben gerichtete z-Achse (0, 0, 1).
# Der genaue Winkel ist auch gar nicht relevant. Hauptsache,
# die „Normale“ zeigt irgendwie aus dem umhüllten Körper heraus
# und nicht in ihn hinein.

with open(ausname,"w") as aus:
    aus.write("solid "+ausname+"\n")
    
    # Geländeoberfläche
    for x in range(ul_e,xmax+1-kl,kl):
      xu = x - ul_e
      for y in range(ul_n,ymax+1-kl,kl):
        yu = y - ul_n
        h1 = D[x,y]
        h2 = D[x+kl,y]
        h3 = D[x,y+kl]
        h4 = D[x+kl,y+kl]
        aus.write("facet normal 0 0 1\n"
                  "outer loop\n"
                  "vertex %i %i %s\n"%(xu, yu, h1) +
                  "vertex %i %i %s\n"%(xu+kl, yu+kl, h4) +
                  "vertex %i %i %s\n"%(xu+kl, yu, h2) +
                  "endloop\n"
                  "endfacet\n")
        aus.write("facet normal 0 0 1\n"
                  "outer loop\n"
                  "vertex %i %i %s\n"%(xu, yu, h1) +
                  "vertex %i %i %s\n"%(xu, yu+kl, h3) +
                  "vertex %i %i %s\n"%(xu+kl, yu+kl, h4) +
                  "endloop\n"
                  "endfacet\n")
        # Was für ein Aufwand für zwei popelige Dreiecke!

    # Die Unterseite und die Seitenflächen wiederholen im Moment
    # die Unterteilung der Oberseite. Dadurch hat die STL-Datei fast
    # doppelt so viele Dreiecke wie eigentlich nur nötig wären.
    # Durch geschickte Aufteilung könnte die Unterseite mit nur zwei
    # Dreiecken realisiert werden, wobei die Seitenflächen mit rund der
    # Hälfte der Dreiecke auskommen könnten. Bei großen Geländesteigungen
    # gibt es da aber ein paar Herausforderungen an den Algorithmus.
        
    # Unterseite
    for x in range(ul_e,xmax+1-kl,kl):
      xu = x - ul_e
      for y in range(ul_n,ymax+1-kl,kl):
        yu = y - ul_n
        aus.write("facet normal 0 0 -1\n"
                  "outer loop\n"
                  "vertex %i %i %.2f\n"%(xu, yu, minh) +
                  "vertex %i %i %.2f\n"%(xu+kl, yu, minh) +
                  "vertex %i %i %.2f\n"%(xu+kl, yu+kl, minh) +
                  "endloop\n"
                  "endfacet\n")
        aus.write("facet normal 0 0 -1\n"
                  "outer loop\n"
                  "vertex %i %i %.2f\n"%(xu, yu, minh) +
                  "vertex %i %i %.2f\n"%(xu+kl, yu+kl, minh) +
                  "vertex %i %i %.2f\n"%(xu, yu+kl, minh) +
                  "endloop\n"
                  "endfacet\n")
        
    # Linke Wand
    for y in range(ul_n,ymax+1-kl,kl):
        yu = y-ul_n
        h1 = D[ul_e,y]
        h2 = D[ul_e,y+kl]
        aus.write("facet normal -1 0 0\n"
                  "outer loop\n"
                  "vertex 0 %i %.2f\n"%(yu, minh) +
                  "vertex 0 %i %.2f\n"%(yu+kl, h2) +
                  "vertex 0 %i %.2f\n"%(yu, h1) +
                  "endloop\n"
                  "endfacet\n")
        aus.write("facet normal -1 0 0\n"
                  "outer loop\n"
                  "vertex 0 %i %.2f\n"%(yu, minh) +
                  "vertex 0 %i %.2f\n"%(yu+kl, minh) +
                  "vertex 0 %i %.2f\n"%(yu+kl, h2) +
                  "endloop\n"
                  "endfacet\n")
        
    # Rechte Wand
    for y in range(ul_n,ymax+1-kl,kl):
        xu = xmax-ul_e
        yu = y-ul_n
        h1 = D[xmax,y]
        h2 = D[xmax,y+kl]
        aus.write("facet normal 1 0 0\n"
                  "outer loop\n"
                  "vertex %i %i %.2f\n" % (xu, yu, minh) +
                  "vertex %i %i %.2f\n" % (xu, yu, h1) +
                  "vertex %i %i %.2f\n" % (xu, yu+kl, h2) +
                  "endloop\n"
                  "endfacet\n")
        aus.write("facet normal 1 0 0\n"
                  "outer loop\n"
                  "vertex %i %i %.2f\n" % (xu, yu, minh) +
                  "vertex %i %i %.2f\n" % (xu, yu+kl, h2) +
                  "vertex %i %i %.2f\n" % (xu, yu+kl, minh) +
                  "endloop\n"
                  "endfacet\n")
        
    # Vordere Wand
    for x in range(ul_e,xmax+1-kl,kl):
        h1 = D[x,ul_n]
        h2 = D[x+kl,ul_n]
        xu = x - ul_e
        aus.write("facet normal 0 -1 0\n"
                  "outer loop\n"
                  "vertex %i 0 %.2f\n" % (xu, minh) +
                  "vertex %i 0 %.2f\n" % (xu, h1) +
                  "vertex %i 0 %.2f\n" % (xu+kl, h2) +
                  "endloop\n"
                  "endfacet\n")
        aus.write("facet normal 0 -1 0\n"
                  "outer loop\n"
                  "vertex %i 0 %.2f\n" % (xu, minh) +
                  "vertex %i 0 %.2f\n" % (xu+kl, h2) +
                  "vertex %i 0 %.2f\n" % (xu+kl, minh) +
                  "endloop\n"
                  "endfacet\n")
        
    # Hintere Wand
    for x in range(ul_e,xmax+1-kl,kl):
        xu = x - ul_e
        yu = ymax - ul_n
        h1 = D[x,ymax]
        h2 = D[x+kl,ymax]
        aus.write("facet normal 0 1 0\n"
                  "outer loop\n"
                  "vertex %i %i %.2f\n"%(xu, yu, minh) +
                  "vertex %i %i %.2f\n"%(xu+kl, yu, h2) +
                  "vertex %i %i %.2f\n"%(xu, yu, h1) +
                  "endloop\n"
                  "endfacet\n")
        aus.write("facet normal 0 1 0\n"
                  "outer loop\n"
                  "vertex %i %i %.2f\n"%(xu, yu, minh) +
                  "vertex %i %i %.2f\n"%(xu+kl, yu, minh) +
                  "vertex %i %i %.2f\n"%(xu+kl, yu, h2) +
                  "endloop\n"
                  "endfacet\n")


### Binäre STL-Datei ###
#
# https://de.wikipedia.org/wiki/STL-Schnittstelle
#
# Die struct-Codes unten bedeuten:
#   "<"   niedrigwertiges Byte voran ("little-endian")
#   "I"   vorzeichenlose Ganzzahl (4 Byte)
#   "12f" 12 Gleitkommawerte (je 4 Byte)
#   "h"   kurze Ganzzahl (2 Byte)

ausname = name+".binär.stl"
log("Schreibe STL-Datei für 3D-Druck (binär): %s" % ausname)

with open(ausname,"wb") as aus:
    # 80 Bytes ungenutzter Header
    aus.write(b'\0' * 80)
    
    # Wie viele Dreiecke hat das Modell insgesamt?
    nx = (xmax - ul_e) // kl 
    ny = (ymax - ul_n) // kl 
    ngesamt = 4 * nx*ny + 4 * nx + 4 * ny
    aus.write(struct.pack('<I', ngesamt))
    
    # Geländeoberfläche
    for x in range(ul_e,xmax+1-kl,kl):
      xu = x - ul_e
      for y in range(ul_n,ymax+1-kl,kl):
        yu = y - ul_n
        h1 = D[x,y]
        h2 = D[x+kl,y]
        h3 = D[x,y+kl]
        h4 = D[x+kl,y+kl]
        aus.write(struct.pack("<12fh",
                              0, 0, 1,
                              xu, yu, h1,
                              xu+kl, yu+kl, h4,
                              xu+kl, yu, h2,
                              0))
        aus.write(struct.pack("<12fh",
                              0, 0, 1,
                              xu, yu, h1,
                              xu, yu+kl, h3,
                              xu+kl, yu+kl, h4,
                              0))
        
    # Unterseite
    for x in range(ul_e,xmax+1-kl,kl):
      xu = x - ul_e
      for y in range(ul_n,ymax+1-kl,kl):
        yu = y - ul_n
        aus.write(struct.pack("<12fh",
                              0, 0, -1,
                              xu, yu, minh,
                              xu+kl, yu+kl, minh,
                              xu+kl, yu, minh,
                              0))
        aus.write(struct.pack("<12fh",
                              0, 0, -1,
                              xu, yu, minh,
                              xu, yu+kl, minh,
                              xu+kl, yu+kl, minh,
                              0))
        
    # Linke Wand
    for y in range(ul_n,ymax+1-kl,kl):
        yu = y-ul_n
        h1 = D[ul_e,y]
        h2 = D[ul_e,y+kl]
        aus.write(struct.pack("<12fh",
                              -1, 0, 0, 
                              0, yu, minh,
                              0, yu+kl, h2,
                              0, yu, h1,
                              0))
        aus.write(struct.pack("<12fh",
                              -1, 0, 0,
                              0, yu, minh,
                              0, yu+kl, minh,
                              0, yu+kl, h2,
                              0))
        
    # Rechte Wand
    xu = xmax-ul_e
    for y in range(ul_n,ymax+1-kl,kl):
        yu = y-ul_n
        h1 = D[xmax,y]
        h2 = D[xmax,y+kl]
        aus.write(struct.pack("<12fh",
                              1, 0, 0, 
                              xu, yu, minh,
                              xu, yu, h1,
                              xu, yu+kl, h2,
                              0))
        aus.write(struct.pack("<12fh",
                              1, 0, 0,
                              xu, yu, minh,
                              xu, yu+kl, h2,
                              xu, yu+kl, minh,
                              0))
        
    # Vordere Wand
    for x in range(ul_e,xmax+1-kl,kl):
        h1 = D[x,ul_n]
        h2 = D[x+kl,ul_n]
        xu = x - ul_e
        aus.write(struct.pack("<12fh",
                              0, -1, 0, 
                              xu, 0, minh,
                              xu, 0, h1,
                              xu+kl, 0, h2,
                              0))
        aus.write(struct.pack("<12fh",
                              0, -1, 0,
                              xu, 0, minh,
                              xu+kl, 0, h2,
                              xu+kl, 0, minh,
                              0))
        
    # Hintere Wand
    yu = ymax - ul_n
    for x in range(ul_e,xmax+1-kl,kl):
        xu = x - ul_e
        h1 = D[x,ymax]
        h2 = D[x+kl,ymax]
        aus.write(struct.pack("<12fh",
                              0, 1, 0, 
                              xu, yu, minh,
                              xu+kl, yu, h2,
                              xu, yu, h1,
                              0))
        aus.write(struct.pack("<12fh",
                              0, 1, 0,
                              xu, yu, minh,
                              xu+kl, yu, minh,
                              xu+kl, yu, h2,
                              0))

log("Programmlauf erfolgreich beendet.\n\n")
print("Die Ausgabedateien können nun weiterverarbeitet werden.")

input("\nProgramm schließen mit [Enter]")
if plt:
    plt.close()
