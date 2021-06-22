#to samo, co w Go_back_N_ARQ, ale wypisuje tylko wynik koncowy

import random #biblioteka do losowania
import time #pomiary czasu

ramki_przeslane = 0 #calkowita liczba przeslanych ramek
ramki_poprawne = 0 #liczba odebranych ramek, ktore zostaly poprawnie zaakceptowane

sekwencja1 = [0, 0] #1 ramka w oknie
sekwencja2 = [0, 1] #2 ramka w oknie
sekwencja3 = [1, 0] #3 ramka w oknie
sekwencja4 = [1, 1] #4 ramka w oknie
numer_ramki = 0 #numer sekwencji, ktorej obecnie oczekuje receiver
numer_sekwencji = [sekwencja1, sekwencja2, sekwencja3, sekwencja4] #dla wygody programisty

klucz = [1, 0, 1, 1] #klucz wielomianu crc

#funkcja raczej dla wygody, bo nie mozemy zrobic np. append(000)
#przesylajac sygnal NAK, przesylany jest ciag bitow 0000110
def append_ACK(ACKK):
    ACKK.append(0)
    ACKK.append(0)
    ACKK.append(0)
    ACKK.append(0)
    ACKK.append(1)
    ACKK.append(1)
    ACKK.append(0)

#funkcja raczej dla wygody, bo nie mozemy zrobic np. append
#przesylajac sygnal NAK, przesylany jest ciag bitow 0010101
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

    for i in range (2, len(pomoc)-3): #XOR
        if(pomoc[i] == 1):
            for j in range (0, 4):
                if(pomoc[i+j] == klucz[j]):
                    pomoc[i+j] = 0
                else:
                    pomoc[i+j] = 1
    for i in range (len(pomoc)-3, len(pomoc)):
        sygnal[i] = pomoc[i]

#2 zamiast 0, bo ignorujemy numer sekwencji
#sprawdzanie, czy wielomian CRC jest poprawny (zarowno wysylajacy, jak i odbierajacy maja dostep do klucza)
def sprawdzanie_CRC(sygnal):
    pomoc = list(sygnal)

    for i in range (2, len(pomoc)-3): #XOR, od 2 bo ignorujemy numer sekwencji
        if(pomoc[i] == 1):
            for j in range (0, 4):
                if(pomoc[i+j] == klucz[j]):
                    pomoc[i+j] = 0
                else:
                    pomoc[i+j] = 1
    for i in range (2, len(pomoc)):
        if(pomoc[i] == 1): return 1 #wynik dzielenia nie jest rowny 0

    return 0 #wynik dzielenia jest rowny 0

#sender, wysylamy ramke, uzywajac bitu parzystosci jako sumy kontrolnej
def wysylanie_sygnalu(sygnal):
    global ACK
    parzystosc = 0
    for i in range (2, len(sygnal)):
        parzystosc += sygnal[i] % 2
    sygnal.append(parzystosc % 2)

    odpowiedz = odbieranie_sygnalu(sygnal)
    zaklocenia(odpowiedz)
    if(str(odpowiedz) == str([0, 0, 0, 0, 1, 1, 0])): ACK = 1

#sender, wysylamy ramke, uzywajac CRC jako sumy kontrolnej
def wysylanie_sygnalu_CRC(sygnal):
    global ACK
    sygnal.append(0) #czterobitowe CRC, czyli dodajemy trzy zera na koniec
    sygnal.append(0)
    sygnal.append(0)
    generowanie_CRC(sygnal)

    odpowiedz = odbieranie_sygnalu_CRC(sygnal) #czekamy na odpowiedz od receivera
    zaklocenia(odpowiedz) #odpowiedz tez moze byc zaklocona
    if(str(odpowiedz) == str([0, 0, 0, 0, 1, 1, 0])): ACK = 1 #sprawdzamy, czy faktycznie otrzymalismy ACK

#sender, wysylamy ramke, uzywajac sumy bitow jako sumy kontrolnej
def wysylanie_sygnalu_suma(sygnal):
    global ACK
    suma = 0
    for i in range (2, len(sygnal)): #od 2, bo ignorujemy numery sekwencji
        suma = suma + sygnal[i]
    suma = bin(suma)[2:].zfill(4)
    for i in range (0, 4):
        sygnal.append(int(suma[i]))

    odpowiedz = odbieranie_sygnalu_suma(sygnal) #czekamy na odpowiedz od receivera
    zaklocenia(odpowiedz) #odpowiedz tez moze byc zaklocona
    if(str(odpowiedz) == str([0, 0, 0, 0, 1, 1, 0])): ACK = 1 #sprawdzamy, czy faktycznie otrzymalismy ACK

#sender, wysylamy ramke, uzywajac powtorzenia ramki jako sumy kontrolnej
def wysylanie_sygnalu_repetition(sygnal): #powtarzamy raz ramke
    global ACK

    for i in range (2, len(sygnal)): #od 2, bo ignorujemy numery sekwencji
        sygnal.append(sygnal[i])

    odpowiedz = odbieranie_sygnalu(sygnal) #czekamy na odpowiedz od receivera
    zaklocenia(odpowiedz) #odpowiedz tez moze byc zaklocona
    if(str(odpowiedz) == str([0, 0, 0, 0, 1, 1, 0])): ACK = 1 #sprawdzamy, czy faktycznie otrzymalismy ACK

def odbieranie_sygnalu(sygnal):
    global a
    ACKK = list("")
    zaklocenia(sygnal)

    if((numer_sekwencji[a])[0] != (numer_sekwencji[numer_ramki])[0]) or ((numer_sekwencji[a])[1] != (numer_sekwencji[numer_ramki])[1]):
        append_NAK(ACKK)
        return ACKK

    parzystosc = 0
    for i in range (2, len(sygnal)-1): #ignorujemy bit parzystosci i numer sekwencji
        parzystosc += sygnal[i] % 2

    if(parzystosc % 2 != sygnal[len(sygnal)-1]):
        append_NAK(ACKK)
        #print("Sygnal zostal zaklocony.")
    else:
        #print("Acknowledged.")
        #ACK = 0b0010101  # NAK
        append_ACK(ACKK)
    "".join(str(ACKK))

    return ACKK

#receiver, odbieramy ramke i sprawdzamy za pomoca wielomianu CRC, czy nie zostala zaklocona
def odbieranie_sygnalu_CRC(sygnal):
    global a
    ACKK = list("")

    if((numer_sekwencji[a])[0] != (numer_sekwencji[numer_ramki])[0]) or ((numer_sekwencji[a])[1] != (numer_sekwencji[numer_ramki])[1]):
        append_NAK(ACKK)
        return ACKK

    zaklocenia(sygnal) #zaklocamy odbierany sygnal

    if(sprawdzanie_CRC(sygnal) == 1): #jezeli wynik dzielenia nie byl rowny 1, czyli jezeli ramka zostala zaklocona
        append_NAK(ACKK)
    else:
        append_ACK(ACKK) #jezeli ramka nie zostala zaklocona
    "".join(str(ACKK))

    return ACKK

#receiver, odbieramy ramke i sprawdzamy za pomoca sumy bitow ramki, czy nie zostala zaklocona
def odbieranie_sygnalu_suma(sygnal):
    global a
    ACKK = list("")
    suma1 = 0 #sprawdzamy, ile wynosi suma bitow w ramce bez dodatkow
    suma2 = 0 #sprawdzamy, ile jest rowna suma bitow z dodanych do ramki elementow
    mnoznik = 8

    if ((numer_sekwencji[a])[0] != (numer_sekwencji[numer_ramki])[0]) or ((numer_sekwencji[a])[1] != (numer_sekwencji[numer_ramki])[1]):
        append_NAK(ACKK)
        return ACKK

    zaklocenia(sygnal) #zaklocamy odbierany sygnal

    for i in range(2, 10): #bo ignorujemy numery sekwencji
        suma1 = suma1 + sygnal[i]

    for i in range(10, 14): #bo ignorujemy numery sekwencji
        suma2 = suma2 + mnoznik * sygnal[i]
        mnoznik = mnoznik // 2

    if(suma1 != suma2): #jezeli suma sie zgadza, to ramka nie zostala zaklocona - w przeciwnym razie zostala zaklocona
        append_NAK(ACKK)
    else:
        append_ACK(ACKK)
    "".join(str(ACKK))

    return ACKK

#receiver, odbieramy ramke i sprawdzamy za pomoca pojedynczego powtorzenia, czy nie zostala zaklocona
def odbieranie_sygnalu_repetition(sygnal):
    global a
    ACKK = list("")
    zaklocenia(sygnal)

    if ((numer_sekwencji[a])[0] != (numer_sekwencji[numer_ramki])[0]) or ((numer_sekwencji[a])[1] != (numer_sekwencji[numer_ramki])[1]):
        append_NAK(ACKK)
        return ACKK

    for i in range(2, 10): #bo ignorujemy numery sekwencji
        if(sygnal[i] != sygnal[i+8]):
            append_NAK(ACKK)
            "".join(str(ACKK))
            return ACKK

    append_ACK(ACKK)
    "".join(str(ACKK))

    return ACKK

#zaklocamy tutaj wysylane i odbierane ramki/sygnaly
def zaklocenia(sygnal):
    for i in range (0, len(sygnal)): #wszystko moze byc zaklocone, czy to numer sekwencji, czy to ramka wlasciwa, czy to suma kontrolna, czy nawet ACK/NAK
        if(random.randint(0,9) == 0): #tutaj zmieniamy szanse na zaklocenie
            if(sygnal[i] == 1): sygnal[i] = 0
            else: sygnal[i] = 1

dlugosc_bit = 1000000 #ile bitow powinna zawierac nasza wiadomosc
informacja = list("") #jakis ciag bitow
informacja = generowanie_sygnalu(informacja, dlugosc_bit) #generujemy losowy ciag bitow
"".join(str(informacja))

x = 0 #indeks obecnej ramki
czas1 = time.time() #rozpoczynamy odliczanie czasu metody
while (x != dlugosc_bit // 8): #dopoki nie wyslalismy wszystkich bitow
    numer_ramki = 0 #numer sekwencji ramki, ktorego oczekuje receiver
    for a in range(0, 4):  # pojedyncze okno
        if(dlugosc_bit > (x + a)*8): #na wypadek, jakby skonczyly sie bity do przeslania przed koncem okna
            ACK = 0 #pomocne dla okreslenia, czy kolejna ramka bedzie przyjeta (zakladajac, ze wszystkie poprzednie byly)
            ramka = informacja[(x + a) * 8:(x + a + 1) * 8] #czyli bierzemy kolejna ramke w obecnym oknie
            oryginalna_ramka = list(ramka) #ramka do sprawdzania, czy suma kontrolna nie przepuscila bledu
            ramka.insert(0, (numer_sekwencji[a])[0]) #dodajemy numer sekwencji
            ramka.insert(1, (numer_sekwencji[a])[1])
            wysylanie_sygnalu_suma(ramka) #przesylamy ramke z dana suma kontrolna
            ramki_przeslane = ramki_przeslane + 1

            if (ACK == 1): numer_ramki = numer_ramki + 1

            if (ACK == 1 and ramka[2:10] == oryginalna_ramka):  # sprawdzamy, czy niepoprawnie odebrana ramka nie uniknela wykrywania bledow
                ramki_poprawne = ramki_poprawne + 1
    x = x + numer_ramki #przechodzimy do pierwszej ramki, ktora zostala znieksztalcona i odrzucona

#podsumowanie wyniku
print("Ilość ramek ogółem: ", len(informacja) // 8) #dlugosc przesylanego ciagu bitow
print("Procent ramek poprawnie odebranych: ", ramki_poprawne / (len(informacja) // 8)) #ile ramek zostalo poprawnie odebranych (tzn. ramka zostala zaakceptowana I nie byla zaklocona)
print("Ile ramek zostało przesłanych w sumie: ", ramki_przeslane) #ile przeslano ramek zaakceptowanych + niezaakceptowanych
print("Czas wykonania metody: ", time.time()-czas1)