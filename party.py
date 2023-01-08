#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ast import parse
from queue import Empty
from re import T, X
from tkinter import SEL
import spade
import asyncio
import random
import time
import re
import string
import copy
import json
from colorama import Fore
from spade.agent import Agent
from spade.behaviour import FSMBehaviour, CyclicBehaviour, State

class Party(Agent):

    def generirajZlato():
        return random.randint(300, 700)

    class PonasanjeParty(FSMBehaviour):
        async def on_start(self):
            print(f"Party: Zapocinjem ponasanje partija: {self.agent.jid}")

    class Generiranje(State):
        async def run(self):
            msg = await self.receive(timeout=30)
            await asyncio.sleep(2)
            if msg.get_metadata("performative") == "upit" and msg.get_metadata("intent") == "zlato":
                print(f"Party: Zlato s kojim raspolažem je {self.agent.zlato} zlatnika")
                await asyncio.sleep(1)
                msg = spade.message.Message(
                to="bornar@jab.im",
                body=(f"{self.agent.zlato}"),
                metadata = {
                    "performative": "party",
                    "ontology": "generiranje",
                    "intent" : "zlato"
                })
                await self.send(msg)
                self.set_next_state("Drazba")

    def stanjeZlata(self, party, zlato):
        print(f"Party: Trenutno stanje zlata je {zlato}")
        print(f"Party se sastoji od:")
        for i in range(len(party)):
            print(party[i][0])



    class Drazba(State):
        async def run(self):
            msgEnemy = None
            msgEnemy = await self.receive(timeout=30)
            await asyncio.sleep(2)
            hp = int(msgEnemy.get_metadata("hp"))
            damage = int(msgEnemy.get_metadata("damage"))
            speed = msgEnemy.get_metadata("speed")
            imaWarrior = 0
            imaPriest = 0
            josRogue = False
            josWarrior = False
            josPriest = False
            josWizard = False
            party = []
            zlato = int(self.agent.zlato)
            
            print(f"Party: Obavezno moram imati bar 1 warriora i 1 priesta\n")
            
            #algoritam odabira mercenarya za party
            for x in party:
                if party[x][0] == "warrior":
                    imaWarrior = imaWarrior + 1
                if party[x][0] == "priest":
                    imaPriest = imaPriest + 1
            if imaWarrior == 0:
                await asyncio.sleep(1)
                print(f"\nParty: Ne sadržim warriora u partyu stoga unajmljujem warriora u party!\n")
                party.append(self.agent.mercenary[0])
                imaWarrior = imaWarrior + 1
                zlato = zlato - 100
                Party.stanjeZlata(self, party, zlato)
            if imaPriest == 0:
                await asyncio.sleep(1)
                print(f"\nParty: Ne sadržim priesta u partyu stoga unajmljujem priesta u party!\n")
                party.append(self.agent.mercenary[1])
                imaPriest = imaPriest + 1
                zlato = zlato - 70
                Party.stanjeZlata(self, party, zlato)
            
            while zlato >= 50:
                #Ukoliko enemy ima velik HP
                if hp >= 5000:
                    josRogue = True
                    josWizard = True
                #Ukoliko enemy ima velik damage
                if damage >= 70:
                    josWarrior = True
                #Ukoliko enemy ima mal HP te je bolje igrat na sigurno bez žurbe
                if hp < 5000:
                    josRogue = False
                if damage >= 70:
                    if speed == "spor":
                        josWarrior = False
                        josRogue = True
                        josWizard = True
                    if speed == "srednji" or speed == "brzi":
                        josWarrior = True
                        josPriest = True
                        josWizard = False
                        josRogue = True

                if damage < 70:
                    josPriest = True
                    josWarrior = True
                    josWizard = True
                    josRogue = True

                if josWarrior == True:
                    if imaWarrior < 2:
                        imaWarrior = imaWarrior + 1
                        await asyncio.sleep(1)
                        print(f"\nParty: Potreban je još jedan warrior u partyu stoga unajmljujem warriora u party!\n")
                        party.append(self.agent.mercenary[0][:])
                        zlato = zlato - 100
                        Party.stanjeZlata(self, party, zlato)

                if josPriest == True:
                    if imaPriest < 2:
                        await asyncio.sleep(1)
                        print(f"\nParty: Potreban je još jedan priest u partyu stoga unajmljujem priesta u party!\n")
                        party.append(self.agent.mercenary[1][:])
                        imaPriest = imaPriest + 1
                        zlato = zlato - 70
                        Party.stanjeZlata(self, party, zlato)

                if josWizard == True and zlato >= 150:
                    await asyncio.sleep(1)
                    print(f"\nParty: Unajmljujem wizarda u party!\n")
                    party.append(self.agent.mercenary[3][:])
                    zlato = zlato - 150
                    Party.stanjeZlata(self, party, zlato)

                elif josRogue == True and zlato >= 50:
                    await asyncio.sleep(1)
                    print(f"\nParty: Unajmljujem rogua u party!\n")
                    party.append(self.agent.mercenary[2][:])
                    zlato = zlato - 50
                    Party.stanjeZlata(self, party, zlato)
                
            self.agent.zlato = zlato
            self.agent.partyGroup = party
            await asyncio.sleep(1)
            print(f"\nParty: Spreman sam za bitku")

            msg = spade.message.Message(
            to="bornar@jab.im",
            body=("spreman"),
            metadata = {
                "performative": "spremnost",
                "ontology": "drazba",
                "intent" : "formiranjeParty",
                "zlato": f"{zlato}",
                "partyGroup": f"{party}",
            })
            await self.send(msg)

            self.set_next_state("Bitka")

    def heal(self, partyZavrsno):
        najslabiji = 0
        najslabijiPozicija = "zdravi"
        pronadeno = False

        for i in range(len(partyZavrsno)):
            if int(partyZavrsno[i][2]) > 0:
                if (int(partyZavrsno[i][4]) - int(partyZavrsno[i][2])) > najslabiji:
                    najslabiji = int(partyZavrsno[i][4]) - int(partyZavrsno[i][2])
                    najslabijiPozicija = i
                    pronadeno = True
        if pronadeno == True:
            return najslabijiPozicija
        
        if pronadeno == False:
            return najslabijiPozicija
    
    #Algoritam za pretvorbu stringa u 2D array
    def stringU2DArray(party):
        partyLista = party.split("], [")
        listaPrava = []
        for i in range(len(partyLista)):
            red = partyLista[i]
            red = red.split(", ")
            listaPrava.insert(i,red)
            listaPrava[i][0] =  str(listaPrava[i][0]).replace('[','').replace(']','').replace('\'','').replace('\"','').replace("'", "")
            listaPrava[i][1] =  str(listaPrava[i][1]).replace('[','').replace(']','').replace('\'','').replace('\"','').replace("'", "")
            listaPrava[i][2] =  str(listaPrava[i][2]).replace('[','').replace(']','').replace('\'','').replace('\"','').replace("'", "")
            listaPrava[i][3] =  str(listaPrava[i][3]).replace('[','').replace(']','').replace('\'','').replace('\"','').replace("'", "")
            listaPrava[i][4] =  str(listaPrava[i][4]).replace('[','').replace(']','').replace('\'','').replace('\"','').replace("'", "")

        return listaPrava

    class Bitka(State):
        async def run(self):
            msg = None
            sumaStete = 0
            partyPocetno = self.agent.partyGroup
            partyZavrsno = copy.deepcopy(partyPocetno)
            await asyncio.sleep(1)

            msg = await self.receive(timeout=30)
            if msg.body == "partyRedPrvi":
                for i in range(len(partyZavrsno)):
                    if partyZavrsno[i][0] != "priest" and partyZavrsno[i][2] != 0:
                        sumaStete = sumaStete + int(partyZavrsno[i][3])
                print(f"Suma štete je: {sumaStete}")

                self.agent.partyGroup = partyZavrsno
                msg = spade.message.Message(
                to="bornar@jab.im",
                body=("RezultatParty"),
                metadata = {
                    "performative": "rezultat",
                    "ontology": "bitka",
                    "intent" : "RezultatParty",
                    "partyGroup": f"{partyZavrsno}",
                    "sumaStete": f"{sumaStete}"
                })
                await self.send(msg)
                self.set_next_state("Bitka")

            if msg.body == "partyRedGotov":
                if msg.get_metadata("rezultat") == "win":
                    self.agent.konacnoStanje = "win"
                    self.set_next_state("Zavrsno")
                if msg.get_metadata("rezultat") == "lose":
                    self.agent.konacnoStanje = "lose"
                    self.set_next_state("Zavrsno")

            if msg.body == "partyRed":
                party = msg.get_metadata("partyGroup")
                listaPretvorena = Party.stringU2DArray(party)
                for i in range(len(listaPretvorena)):
                    if listaPretvorena[i][0] != "priest" and int(listaPretvorena[i][2]) > 0:
                        sumaStete = sumaStete + int(listaPretvorena[i][3])
                    if listaPretvorena[i][0] == "priest" and int(listaPretvorena[i][2]) > 0:
                        najslabijiPozicija = Party.heal(self, listaPretvorena)
                        if najslabijiPozicija == "zdravi":
                            d = None
                        if najslabijiPozicija != "zdravi":
                            await asyncio.sleep(1)
                            print(f"{listaPretvorena[i][0]} ({i}.): Healam {listaPretvorena[najslabijiPozicija][0]} na poziciji {najslabijiPozicija}.")
                            listaPretvorena[najslabijiPozicija][2] = int(listaPretvorena[najslabijiPozicija][2]) + 40

                print(f"Party: Nanosimo {sumaStete} bodova štete")
                msg = spade.message.Message(
                to="bornar@jab.im",
                body=("RezultatParty"),
                metadata = {
                    "performative": "rezultat",
                    "ontology": "bitka",
                    "intent" : "RezultatParty",
                    "partyGroup": f"{listaPretvorena}",
                    "sumaStete": f"{sumaStete}"
                })
                await self.send(msg)
                self.set_next_state("Bitka")
            
    class Zavrsno(State):
        async def run(self):
            await asyncio.sleep(1)
            if self.agent.konacnoStanje == "win":
                print("\nParty: Pobijedio sam!")
            
            if self.agent.konacnoStanje == "lose":
                print("\nParty: Izgubio sam!")

    async def setup(self):
        print("Party agent zapocinje")

        fsm = self.PonasanjeParty()

        fsm.add_state(name="Generiranje", state=self.Generiranje(), initial=True)
        fsm.add_state(name="Drazba", state=self.Drazba())
        fsm.add_state(name="Bitka", state=self.Bitka())
        fsm.add_state(name="Zavrsno", state=self.Zavrsno())

        fsm.add_transition(source="Generiranje", dest="Drazba")
        fsm.add_transition(source="Drazba", dest="Bitka")
        fsm.add_transition(source="Bitka", dest="Bitka")
        fsm.add_transition(source="Bitka", dest="Zavrsno")
        fsm.add_transition(source="Zavrsno", dest="Generiranje")

        self.add_behaviour(fsm)

        self.zlato = random.randint(400, 800)
        self.konacnoStanje = ""
        #[klasa, gold, HP, damage/heal, maxHP]
        self.mercenary = [["warrior", 100, 200, 50, 200],["priest", 70, 100, 40, 100],["rogue", 50, 100, 75, 100],["wizard", 150, 80, 200, 80]]
        self.partyGroup = []
