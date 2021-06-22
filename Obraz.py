#przestarzaly kod, z czasow generowania obrazow do prezentacji
#postanowilismy go uwzglednic, poniewaz w zasadzie dziala dobrze (choc nieoptymalnie)
#modyfikacja obrazu tylko dla Stop and wait, bo (jezeli dobrze rozumiemy) inne wariacje ARQ wykonaja to tak samo dobrze, tylko po prostu wolniej/szybciej

from PIL import Image
import random
import time

klucz = [1, 0, 1, 1]
ramki_poprawne = 0
ramki_przeslane = 0
sequence_number = 0

def generowanie_CRC(sygnal):
    pomoc = list(sygnal)

    for i in range (0, len(pomoc)-3): #XOR
        if(pomoc[i] == 1):
            for j in range (0, 4):
                if(pomoc[i+j] == klucz[j]):
                    pomoc[i+j] = 0
                else:
                    pomoc[i+j] = 1
    for i in range (len(pomoc)-3, len(pomoc)):
        sygnal[i] = pomoc[i]

def sprawdzanie_CRC(sygnal):
    pomoc = list(sygnal)

    for i in range (0, len(pomoc)-3): #XOR
        if(pomoc[i] == 1):
            for j in range (0, 4):
                if(pomoc[i+j] == klucz[j]):
                    pomoc[i+j] = 0
                else:
                    pomoc[i+j] = 1
    for i in range (0, len(pomoc)):
        if(pomoc[i] == 1): return 1 #wynik dzielenia nie jest rowny 0

    return 0 #wynik dzielenia jest rowny 0

def wysylanie_sygnalu(sygnal):
    global ACK
    parzystosc = 0
    for i in range (0, len(sygnal)):
        parzystosc = (parzystosc + sygnal[i]) % 2
    sygnal.append(parzystosc)

    odpowiedz = odbieranie_sygnalu(sygnal)
    zaklocenia(odpowiedz)
    if(str(odpowiedz) == str([0, 0, 0, 0, 1, 1, 0])): ACK = 1
    return sygnal

def wysylanie_sygnalu_CRC(sygnal):
    global ACK
    sygnal.append(0) #czterobitowe CRC, czyli dodajemy trzy zera na koniec
    sygnal.append(0)
    sygnal.append(0)
    generowanie_CRC(sygnal)

    odpowiedz = odbieranie_sygnalu_CRC(sygnal)
    zaklocenia(odpowiedz)
    if(str(odpowiedz) == str([0, 0, 0, 0, 1, 1, 0])): ACK = 1
    return sygnal

def wysylanie_sygnalu_suma(sygnal):
    global ACK
    suma = 0
    for i in range (0, len(sygnal)):
        suma = suma + sygnal[i]
    suma = bin(suma)[2:].zfill(4)
    for i in range (0, 4):
        sygnal.append(int(suma[i]))

    odpowiedz = odbieranie_sygnalu_suma(sygnal)
    zaklocenia(odpowiedz)
    if(str(odpowiedz) == str([0, 0, 0, 0, 1, 1, 0])): ACK = 1
    return sygnal

def wysylanie_sygnalu_repetition(sygnal): #powtarzamy raz ramke
    global ACK
    for i in range(0, len(sygnal)):
        sygnal.append(sygnal[i])

    odpowiedz = odbieranie_sygnalu(sygnal)
    zaklocenia(odpowiedz)
    if(str(odpowiedz) == str([0, 0, 0, 0, 1, 1, 0])): ACK = 1
    return sygnal

def odbieranie_sygnalu(sygnal):
    ACKK = list("")
    zaklocenia(sygnal)

    parzystosc = 0
    for i in range (0, len(sygnal)-1):
        parzystosc = (parzystosc + sygnal[i]) % 2

    if(parzystosc % 2 != sygnal[len(sygnal)-1]):
        ACKK.append(0)
        ACKK.append(0)
        ACKK.append(1)
        ACKK.append(0)
        ACKK.append(1)
        ACKK.append(0)
        ACKK.append(1)
    else:
        ACKK.append(0)
        ACKK.append(0)
        ACKK.append(0)
        ACKK.append(0)
        ACKK.append(1)
        ACKK.append(1)
        ACKK.append(0)
    "".join(str(ACKK))

    return ACKK

def odbieranie_sygnalu_CRC(sygnal):
    ACKK = list("")
    zaklocenia(sygnal)

    if(sprawdzanie_CRC(sygnal) == 1):
        ACKK.append(0)
        ACKK.append(0)
        ACKK.append(1)
        ACKK.append(0)
        ACKK.append(1)
        ACKK.append(0)
        ACKK.append(1)
    else:
        ACKK.append(0)
        ACKK.append(0)
        ACKK.append(0)
        ACKK.append(0)
        ACKK.append(1)
        ACKK.append(1)
        ACKK.append(0)
    "".join(str(ACKK))

    return ACKK

def odbieranie_sygnalu_suma(sygnal):
    ACKK = list("")
    suma1 = 0 #sprawdzamy, ile wynosi suma bitow w ramce bez dodatkow
    suma2 = 0 #sprawdzamy, ile jest rowna suma bitow z dodanych do ramki elementow
    mnoznik = 8

    zaklocenia(sygnal)

    for i in range(0, 8):
        suma1 = suma1 + sygnal[i]

    for i in range(8, 12):
        suma2 = suma2 + mnoznik * sygnal[i]
        mnoznik = mnoznik // 2

    if(suma1 != suma2):
        ACKK.append(0)
        ACKK.append(0)
        ACKK.append(1)
        ACKK.append(0)
        ACKK.append(1)
        ACKK.append(0)
        ACKK.append(1)
    else:
        ACKK.append(0)
        ACKK.append(0)
        ACKK.append(0)
        ACKK.append(0)
        ACKK.append(1)
        ACKK.append(1)
        ACKK.append(0)
    "".join(str(ACKK))

    return ACKK

def odbieranie_sygnalu_repetition(sygnal):
    ACKK = list("")

    zaklocenia(sygnal)

    for i in range(0, 8):
        if(sygnal[i] != sygnal[i+8]):
            ACKK.append(0)
            ACKK.append(0)
            ACKK.append(1)
            ACKK.append(0)
            ACKK.append(1)
            ACKK.append(0)
            ACKK.append(1)
            "".join(str(ACKK))
            return ACKK

    #print("Acknowledged.")
    #ACK = 0b0010101  # NAK
    ACKK.append(0)
    ACKK.append(0)
    ACKK.append(0)
    ACKK.append(0)
    ACKK.append(1)
    ACKK.append(1)
    ACKK.append(0)
    "".join(str(ACKK))

    return ACKK


def zaklocenia(sygnal):
    for i in range (0, len(sygnal)): #chcemy zaklocac takze bit parzystosci
        if(random.randint(0,999) == 0):
            if(sygnal[i] == 1): sygnal[i] = 0
            else: sygnal[i] = 1

#funkcja pomocnicza
def toList(liczba):
    c = str(liczba)
    lista = []
    for i in range (0, len(c)):
        lista.append(int(c[i]))
    return lista

#funkcja pomocnicza
def frameToInt(lista):
    liczba = 0
    potega = 128
    for i in range (0, len(lista)):
        liczba = liczba + lista[i]*potega
        potega = potega // 2
    return liczba

try:
    img = Image.open("picture.jpg")
    pixelMap = img.load()

    czas1 = time.time()
    for i in range(img.size[0]): #wczytujemy wszystkie piksele obrazu (w wypadku naszego obrazu jest to ok. 750 tyś pikseli)
        for j in range(img.size[1]): #mozna zrobic lepsza petle, ale coz
            ACK = 0
            #przesylamy bity R piksela
            while(ACK == 0): #przesylaj dopoki nie dostaniesz ACK
                #R na pewno nie bedzie undefined, to samo G i B
                R = (bin(pixelMap[i, j][0])[2:]).zfill(8)
                R = toList(R) #zamieniamy liczbę na listę
                R = wysylanie_sygnalu_repetition(R)  # wysylamy kolejna ramke
            ACK = 0
            #przesylamy bity R piksela
            while (ACK == 0):  # przesylaj dopoki nie dostaniesz ACK
                G = (bin(pixelMap[i, j][1])[2:]).zfill(8)
                G = toList(G)  # zamieniamy liczbę na listę
                G = wysylanie_sygnalu_repetition(G)  # wysylamy kolejna ramke
            ACK = 0
            #przesylamy bity R piksela
            while (ACK == 0):  # przesylaj dopoki nie dostaniesz ACK
                B = (bin(pixelMap[i, j][2])[2:]).zfill(8)
                B = toList(B)  # zamieniamy liczbę na listę
                B = wysylanie_sygnalu_repetition(B)  # wysylamy kolejna ramke
            pixelMap[i, j] = (frameToInt(R), frameToInt(G), frameToInt(B)) #reprezentacja tego, co otrzymał receiver
    print(time.time()-czas1)
    img.show() #pokazujemy rezultat pracy programu

    img.save("obraz1.jpg") #zapisujemy obraz pod nazwa obraz1
except IOError:
    pass
