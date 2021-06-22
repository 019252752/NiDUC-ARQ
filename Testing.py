#to samo, co Stop_and_wait_ARQ, ale bez wypisywania czegokolwiek oprocz wyniku koncowego

import random #biblioteka do losowania
import time #pomiary czasu

klucz = [1, 0, 1, 1] #klucz crc
ramki_poprawne = 0 #liczba odebranych ramek, ktore zostaly poprawnie zaakceptowane
ramki_przeslane = 0 #calkowita liczba przeslanych ramek

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
    for i in range (0, len(pomoc)):
        if(pomoc[i] == 1): return 1 #wynik dzielenia nie jest rowny 0

    return 0 #wynik dzielenia jest rowny 0

#sender, wysylamy ramke, uzywajac bitu parzystosci jako sumy kontrolnej
def wysylanie_sygnalu(sygnal):
    global ACK
    parzystosc = 0
    for i in range (0, len(sygnal)):
        parzystosc = (parzystosc + sygnal[i]) % 2
    sygnal.append(parzystosc)

    odpowiedz = odbieranie_sygnalu(sygnal) #czekamy na odpowiedz od receivera
    zaklocenia(odpowiedz) #odpowiedz tez moze byc zaklocona
    if(str(odpowiedz) == str([0, 0, 0, 0, 1, 1, 0])): ACK = 1 #sprawdzamy, czy faktycznie otrzymalismy ACK

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
    for i in range (0, len(sygnal)):
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

    for i in range (0, len(sygnal)):
        sygnal.append(sygnal[i])

    odpowiedz = odbieranie_sygnalu(sygnal) #czekamy na odpowiedz od receivera
    zaklocenia(odpowiedz) #odpowiedz tez moze byc zaklocona
    if(str(odpowiedz) == str([0, 0, 0, 0, 1, 1, 0])): ACK = 1 #sprawdzamy, czy faktycznie otrzymalismy ACK

#receiver, odbieramy ramke i sprawdzamy za pomoca bitu parzystosci, czy nie zostala zaklocona
def odbieranie_sygnalu(sygnal):
    ACKK = list("")
    zaklocenia(sygnal) #zaklocamy odbierany sygnal

    parzystosc = 0
    for i in range (0, len(sygnal)-1):
        parzystosc = (parzystosc + sygnal[i]) % 2

    if(parzystosc % 2 != sygnal[len(sygnal)-1]):
        append_NAK(ACKK) #jezeli sygnal zostal zaklocony
    else:
        append_ACK(ACKK) #jezeli sygnal nie zostal zaklocony
    "".join(str(ACKK))

    return ACKK

#receiver, odbieramy ramke i sprawdzamy za pomoca wielomianu CRC, czy nie zostala zaklocona
def odbieranie_sygnalu_CRC(sygnal):
    ACKK = list("")
    zaklocenia(sygnal) #zaklocamy odbierany sygnal

    if(sprawdzanie_CRC(sygnal) == 1): #jezeli wynik dzielenia nie byl rowny 1, czyli jezeli ramka zostala zaklocona
        append_NAK(ACKK)
    else:
        append_ACK(ACKK) #jezeli ramka nie zostala zaklocona
    "".join(str(ACKK))

    return ACKK

#receiver, odbieramy ramke i sprawdzamy za pomoca sumy bitow ramki, czy nie zostala zaklocona
def odbieranie_sygnalu_suma(sygnal):
    ACKK = list("")
    suma1 = 0 #sprawdzamy, ile wynosi suma bitow w ramce bez dodatkow
    suma2 = 0 #sprawdzamy, ile jest rowna suma bitow z dodanych do ramki elementow
    mnoznik = 8

    zaklocenia(sygnal) #zaklocamy odbierany sygnal

    for i in range(0, 8):
        suma1 = suma1 + sygnal[i]

    for i in range(8, 12):
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
    ACKK = list("")

    zaklocenia(sygnal)

    for i in range(0, 8):
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
        if(random.randint(0, 19) == 0): #tutaj zmieniamy szanse na zaklocenie
            if(sygnal[i] == 1): sygnal[i] = 0
            else: sygnal[i] = 1

dlugosc_bit = 1000000 #ile bitow powinna zawierac nasza wiadomosc
informacja = list("") #jakis ciag bitow
informacja = generowanie_sygnalu(informacja, dlugosc_bit) #generujemy losowy ciag bitow
"".join(str(informacja))
czas1 = time.time() #rozpoczynamy odmierzanie czasu
for i in range (0, dlugosc_bit // 8): #wczytujemy pojedyncza ramke
    ACK = 0 #w nowej iteracji petli jeszcze nie otrzymalismy ACKA
    while(ACK == 0): #dopoki receiver nie otrzyma wlasciwej ramki
        ramka = informacja[i * 8:(i + 1) * 8]
        oryginalna_ramka = list(ramka)  # do sprawdzania, czy zaakceptowana zostala odpowiednia ramka
        wysylanie_sygnalu_suma(ramka) #wysylamy kolejna ramke, zmieniaj tu sposob wysylania
        ramki_przeslane = ramki_przeslane + 1
        if(ACK == 1 and ramka[:8] == oryginalna_ramka): #sprawdzamy, czy niepoprawnie odebrana ramka nie uniknela wykrywania bledow
            ramki_poprawne = ramki_poprawne + 1


#podsumowanie wynikow
print("Ilość ramek ogółem: ", len(informacja) // 8) #dlugosc przesylanego ciagu bitow
print("Procent ramek poprawnie odebranych: ", ramki_poprawne / (len(informacja) // 8)) #jaki procent ramek zostal poprawnie odebranych (tzn. ramka zostala zaakceptowana I nie byla zaklocona)
print("Ile razy ramki zostały przesłane: ", ramki_przeslane) #ile przeslano ramek zaakceptowanych + niezaakceptowanych
print("Czas wykonania metody: ", time.time()-czas1) #czas dzialania metody