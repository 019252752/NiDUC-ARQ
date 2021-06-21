import random #biblioteka do losowania
import time #pomiary czasu

klucz = [1, 0, 1, 1]
ramki_poprawne = 0
ramki_przeslane = 0
sequence_number = 0

def append_ACK(ACKK):
    ACKK.append(0)
    ACKK.append(0)
    ACKK.append(0)
    ACKK.append(0)
    ACKK.append(1)
    ACKK.append(1)
    ACKK.append(0)

def append_NAK(ACKK):
    ACKK.append(0)
    ACKK.append(0)
    ACKK.append(1)
    ACKK.append(0)
    ACKK.append(1)
    ACKK.append(0)
    ACKK.append(1)

#generowanie losowego sygnalu, ktory bedziemy przesylac
def generowanie_sygnalu(ramka, rozmiar_ramki): #ramka to sygnał, który będziemy przesyłać; rozmiar_ramki to długość tego sygnału w bitach
    for i in range (0, rozmiar_ramki):
        ramka.append(random.randint(0,1))
    return ramka

#generowanie wielomianu CRC
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

#sprawdzanie, czy wielomian CRC jest poprawny (zarowno wysylajacy, jak i odbierajacy maja dostep do klucza)
def sprawdzanie_CRC(sygnal):
    pomoc = list(sygnal)

    for i in range (0, len(pomoc)-3): #XOR
        if(pomoc[i] == 1):
            for j in range (0, 4):
                if(pomoc[i+j] == klucz[j]):
                    pomoc[i+j] = 0
                else:
                    pomoc[i+j] = 1
    print("aaa", pomoc)
    for i in range (0, len(pomoc)):
        if(pomoc[i] == 1): return 1 #wynik dzielenia nie jest rowny 0

    return 0 #wynik dzielenia jest rowny 0

#sender, wysylamy sygnal, uzywajac bitu parzystosci jako sumy kontrolnej
def wysylanie_sygnalu(sygnal):
    global ACK
    parzystosc = 0
    for i in range (0, len(sygnal)):
        parzystosc = (parzystosc + sygnal[i]) % 2
    sygnal.append(parzystosc)
    print("Sygnal oryginalny: ")
    print(sygnal)

    odpowiedz = odbieranie_sygnalu(sygnal) #czekamy na odpowiedz od receivera
    zaklocenia(odpowiedz) #odpowiedz tez moze byc zaklocona
    if(str(odpowiedz) == str([0, 0, 0, 0, 1, 1, 0])): ACK = 1 #sprawdzamy, czy faktycznie otrzymalismy ACK

#sender, wysylamy sygnal, uzywajac CRC jako sumy kontrolnej
def wysylanie_sygnalu_CRC(sygnal):
    global ACK
    sygnal.append(0) #czterobitowe CRC, czyli dodajemy trzy zera na koniec
    sygnal.append(0)
    sygnal.append(0)
    generowanie_CRC(sygnal)
    print("Sygnal oryginalny: ")
    print(sygnal)

    odpowiedz = odbieranie_sygnalu_CRC(sygnal)
    zaklocenia(odpowiedz)
    if(str(odpowiedz) == str([0, 0, 0, 0, 1, 1, 0])): ACK = 1

def wysylanie_sygnalu_suma(sygnal):
    global ACK
    suma = 0
    for i in range (0, len(sygnal)):
        suma = suma + sygnal[i]
    suma = bin(suma)[2:].zfill(4)
    for i in range (0, 4):
        sygnal.append(int(suma[i]))
    print("Sygnal oryginalny: ")
    print(sygnal)

    odpowiedz = odbieranie_sygnalu_suma(sygnal)
    zaklocenia(odpowiedz)
    if(str(odpowiedz) == str([0, 0, 0, 0, 1, 1, 0])): ACK = 1

def wysylanie_sygnalu_repetition(sygnal): #powtarzamy raz ramke
    global ACK

    for i in range (0, len(sygnal)):
        sygnal.append(sygnal[i])
    print("Sygnal oryginalny: ")
    print(sygnal)

    odpowiedz = odbieranie_sygnalu(sygnal)
    zaklocenia(odpowiedz)
    if(str(odpowiedz) == str([0, 0, 0, 0, 1, 1, 0])): ACK = 1

def odbieranie_sygnalu(sygnal):
    ACKK = list("")
    zaklocenia(sygnal)
    print("Sygnal odebrany: ")
    print(sygnal)

    parzystosc = 0
    for i in range (0, len(sygnal)-1):
        parzystosc = (parzystosc + sygnal[i]) % 2

    print(parzystosc % 2, sygnal[len(sygnal)-1])
    if(parzystosc % 2 != sygnal[len(sygnal)-1]):
        append_NAK(ACKK)
        #print("Sygnal zostal zaklocony.")
    else:
        #print("Acknowledged.")
        #ACK = 0b0010101  # NAK
        append_ACK(ACKK)
    "".join(str(ACKK))

    return ACKK

def odbieranie_sygnalu_CRC(sygnal):
    ACKK = list("")
    zaklocenia(sygnal)
    print("Sygnal odebrany: ")
    print(sygnal)

    if(sprawdzanie_CRC(sygnal) == 1): #jezeli wynik dzielenia nie byl rowny 1
        append_NAK(ACKK)
    else:
        append_ACK(ACKK)
    "".join(str(ACKK))

    return ACKK

def odbieranie_sygnalu_suma(sygnal):
    ACKK = list("")
    suma1 = 0 #sprawdzamy, ile wynosi suma bitow w ramce bez dodatkow
    suma2 = 0 #sprawdzamy, ile jest rowna suma bitow z dodanych do ramki elementow
    mnoznik = 8

    zaklocenia(sygnal)
    print("Sygnal odebrany: ")
    print(sygnal)

    for i in range(0, 8):
        suma1 = suma1 + sygnal[i]

    for i in range(8, 12):
        suma2 = suma2 + mnoznik * sygnal[i]
        mnoznik = mnoznik // 2

    print(suma1)
    print(suma2)

    if(suma1 != suma2):
        append_NAK(ACKK)
    else:
        append_ACK(ACKK)
    "".join(str(ACKK))

    return ACKK

def odbieranie_sygnalu_repetition(sygnal):
    ACKK = list("")

    zaklocenia(sygnal)
    print("Sygnal odebrany: ")
    print(sygnal)

    for i in range(0, 8):
        if(sygnal[i] != sygnal[i+8]):
            append_NAK(ACKK)
            "".join(str(ACKK))
            return ACKK

    append_ACK(ACKK)
    "".join(str(ACKK))

    return ACKK


def zaklocenia(sygnal):
    for i in range (0, len(sygnal)): #chcemy zaklocac takze bit parzystosci
        if(random.randint(0, 19) == 0):
            if(sygnal[i] == 1): sygnal[i] = 0
            else: sygnal[i] = 1

dlugosc_bit = 64 #ile bitow powinna zawierac nasza wiadomosc
informacja = list("")
informacja = generowanie_sygnalu(informacja, dlugosc_bit)
"".join(str(informacja))
print(informacja)
czas1 = time.time()
print(czas1)
for i in range (0, dlugosc_bit // 8):
    ACK = 0
    while(ACK == 0):
        ramka = informacja[i * 8:(i + 1) * 8]
        oryginalna_ramka = list(ramka)  # do sprawdzania, czy zaakceptowana zostala odpowiednia ramka
        print("Ramka numer " + str(i+1))
        wysylanie_sygnalu_repetition(ramka) #wysylamy kolejna ramke, zmieniaj tu sposob wysylania
        ramki_przeslane = ramki_przeslane + 1
        print(ACK)
        print(ramka[:8])
        print(oryginalna_ramka)
        if(ACK == 1 and ramka[:8] == oryginalna_ramka): #sprawdzamy, czy niepoprawnie odebrana ramka nie uniknela wykrywania bledow
            ramki_poprawne = ramki_poprawne + 1
        sequence_number = (sequence_number + 1) % 2 #ustawiamy kolejny numer sekwencji, ktorego oczekujemy
        print()
        print()
        print()

#podsumowanie wyniku
print("Ilość ramek ogółem: ", len(informacja) // 8)
print("Ilość ramek poprawnie odebranych: ", ramki_poprawne)
print("Ile razy ramki zostały przesłane: ", ramki_przeslane)

print("Czas wykonania metody: ", time.time()-czas1)