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
import json
from spade.agent import Agent
from spade.behaviour import FSMBehaviour, CyclicBehaviour, State
from numpy.random import permutation


class Enemy(Agent):

    def odrediHP(self, naziv):
        if naziv == self.imena[0]:
            return 7000
        if naziv == self.imena[1]:
            return 3000
        if naziv == self.imena[2]:
            return 5000
        if naziv == self.imena[3]:
            return 2000

    def odrediDamage(self, naziv):
        if naziv == self.imena[0]:
            return 70
        if naziv == self.imena[1]:
            return 50
        if naziv == self.imena[2]:
            return 80
        if naziv == self.imena[3]:
            return 40

    def odrediSpeed(self, naziv):
        if naziv == self.imena[0]:
            return "spor"
        if naziv == self.imena[1]:
            return "srednji"
        if naziv == self.imena[2]:
            return "srednji"
        if naziv == self.imena[3]:
            return "brzi"
    
    class PonasanjeEnemy(FSMBehaviour):
        async def on_start(self):
            print(f"Enemy: Zapocinjem ponasanje enemija: {self.agent.jid}")

    class Generiranje(State):
        async def run(self):
            msg = None
            msg = await self.receive(timeout=40)
            await asyncio.sleep(2)
            if msg.get_metadata("performative") == "upit" and msg.get_metadata("intent") == "informacija":
                naziv = str(self.agent.naziv).replace('[','').replace(']','').replace('\'','').replace('\"','')
                
                print(f"Enemy: Moje ime je {naziv}\n")
                await asyncio.sleep(1)
                msg = spade.message.Message(
                to="bornar@jab.im",
                body=(f"{naziv}"),
                metadata = {
                    "performative": "enemy",
                    "ontology": "generiranje",
                    "intent" : "informacija",
                    "naziv": f"{naziv}",
                    "hp": f"{self.agent.hp}",
                    "damage": f"{self.agent.damage}",
                    "speed": f"{self.agent.speed}"
                })
                await self.send(msg)
                self.set_next_state("Bitka")

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

    #Algoritam za random napad na party membera ovisno o klasi (drugačija aggro šansa)
    def napad(party):
        pronaden = False
        counter = 0
        meta = None
        while counter <= 90:
            mercenary = ["warrior", "priest", "rogue", "wizard"]
            odluka = random.choices(mercenary, weights=(120, 20, 50, 20), k=1)
            odluka = str(odluka).replace('[','').replace(']','').replace('\'','').replace('\"','').replace("'", "")
            for i in permutation(len(party)):
                if str(party[i][0]).replace('[','').replace(']','').replace('\'','').replace('\"','').replace("'", "") == odluka and pronaden == False and int(party[i][2]) > 0:
                    pronaden = True
                    meta = i
            counter += 1
        return meta    
    

    class Bitka(State):
        async def run(self):
            msgBitka = None
            await asyncio.sleep(1)
            msgBitka = await self.receive(timeout=30)
            await asyncio.sleep(1)

            if msgBitka.body == "enemyRedGotov":
                if msgBitka.get_metadata("rezultat") == "win":
                    self.agent.konacnoStanje = "win"
                    self.set_next_state("Zavrsno")
                if msgBitka.get_metadata("rezultat") == "lose":
                    self.agent.konacnoStanje = "lose"
                    self.set_next_state("Zavrsno")

            if msgBitka.body == "enemyRed":
                if msgBitka.get_metadata("ontology") == "bitka" and msgBitka.get_metadata("intent") == "RezultatParty":
                    party = msgBitka.get_metadata("partyGroup")
                    listaPretvorena = Enemy.stringU2DArray(party)

                    if self.agent.speed == "spor":
                        for i in range(1):
                            meta = Enemy.napad(listaPretvorena)
                            if meta != None:
                                listaPretvorena[meta][2] = int(listaPretvorena[meta][2]) - int(self.agent.damage)
                                if int(listaPretvorena[meta][2]) < 0:
                                    listaPretvorena[meta][2] = int(0)
                                if int(listaPretvorena[meta][2]) >= 0:
                                    await asyncio.sleep(1)
                                    print(f"Enemy: Napadam {listaPretvorena[meta][0]} (nalazi se na indexu broj {meta}), njegov HP je sada {listaPretvorena[meta][2]}")

                    if self.agent.speed == "srednji":
                        for i in range(2):
                            meta = Enemy.napad(listaPretvorena)
                            if meta != None:
                                listaPretvorena[meta][2] = int(listaPretvorena[meta][2]) - int(self.agent.damage)
                                if int(listaPretvorena[meta][2]) < 0:
                                    listaPretvorena[meta][2] = 0
                                if int(listaPretvorena[meta][2]) >= 0:
                                    await asyncio.sleep(1)
                                    print(f"Enemy: Napadam {listaPretvorena[meta][0]} (nalazi se na indexu broj {meta}), njegov HP je sada {listaPretvorena[meta][2]}")

                    if self.agent.speed == "brzi":
                        for i in range(3):
                            meta = Enemy.napad(listaPretvorena)
                            if meta != None:
                                listaPretvorena[meta][2] = int(listaPretvorena[meta][2]) - int(self.agent.damage)
                                if int(listaPretvorena[meta][2]) < 0:
                                    listaPretvorena[meta][2] = int(0)
                                if int(listaPretvorena[meta][2]) >= 0:
                                    await asyncio.sleep(1)
                                    print(f"Enemy: Napadam {listaPretvorena[meta][0]} (nalazi se na indexu broj {meta}), njegov HP je sada {listaPretvorena[meta][2]}")

                    for i in range(len(listaPretvorena)):
                        await asyncio.sleep(1)
                        print(f"\n {i}. {listaPretvorena[i][0]} {listaPretvorena[i][2]}/{listaPretvorena[i][4]} HP")
                    
                    await asyncio.sleep(2)


                    msg = spade.message.Message(
                    to="bornar@jab.im",
                    body=("enemyRezultat"),
                    metadata = {
                        "performative": "rezultat",
                        "ontology": "bitka",
                        "intent" : "RezultatEnemy",
                        "partyGroup": f"{listaPretvorena}",
                    })
                    await self.send(msg)
                    self.set_next_state("Bitka")

    class Zavrsno(State):
        async def run(self):
            await asyncio.sleep(1)
            if self.agent.konacnoStanje == "win":
                print("\nEnemy: Pobijedio sam!")
            
            if self.agent.konacnoStanje == "lose":
                print("\nEnemy: Izgubio sam!")
    


    async def setup(self):
        print("Enemy agent zapocinje")

        fsm = self.PonasanjeEnemy()

        fsm.add_state(name="Generiranje", state=self.Generiranje(), initial=True)
        fsm.add_state(name="Bitka", state=self.Bitka())
        fsm.add_state(name="Zavrsno", state=self.Zavrsno())


        fsm.add_transition(source="Generiranje", dest="Generiranje")
        fsm.add_transition(source="Generiranje", dest="Bitka")
        fsm.add_transition(source="Bitka", dest="Bitka")
        fsm.add_transition(source="Bitka", dest="Zavrsno")
        fsm.add_transition(source="Zavrsno", dest="Generiranje")

        self.add_behaviour(fsm)

        self.imena = ["Starscourge Radahn", "Margit The Fell Omen", "Maliketh, the Black Blade", "Commander Nial"]

        #self.naziv=random.choices(self.imena, weights=(25,25,25,25), k=1)
        self.naziv = self.imena[2]
        self.naziv = str(self.naziv).replace('[','').replace(']','').replace('\'','').replace('\"','')
        self.hp = self.odrediHP(self.naziv)
        self.damage = self.odrediDamage(self.naziv)
        self.speed = self.odrediSpeed(self.naziv)
        self.konacnoStanje = ""





