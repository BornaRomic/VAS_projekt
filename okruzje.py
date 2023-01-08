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
from enemy import Enemy
from spade.agent import Agent
from spade.behaviour import FSMBehaviour, CyclicBehaviour, State

class Okruzje(Agent):

    class PonasanjeOkruzje(FSMBehaviour):
        async def on_start(self):
            print(f"Okruzje: Zapocinjem ponasanje okruzja: {self.agent.jid}")

    class Generiranje(State):
        async def run(self):
            msg = None
            await asyncio.sleep(5)
            print("\nOkružje: Party, zanima me s koliko zlatnika raspolažeš?")
            msg = spade.message.Message(
            to="bornaagent@jab.im",
            body=("upit"),
            metadata = {
                "performative": "upit",
                "ontology": "generiranje",
                "intent" : "zlato"
            })
            await self.send(msg)

            msgParty = await self.receive(timeout=30)
            #await asyncio.sleep(2)
            if msgParty.get_metadata("performative") == "party" and msgParty.get_metadata("intent") == "zlato":
                self.agent.zlatoPartya = msgParty.body

            if self.agent.zlatoPartya != 0:
                print("\nOkruzje: Kako bi rasporedio svoje zlato potrebno je da se informiraš o neprijatelju")
                msg = spade.message.Message(
                to="bornaagent2@jab.im",
                body=("upit"),
                metadata = {
                    "performative": "upit",
                    "ontology": "generiranje",
                    "intent" : "informacija"
                })
                await self.send(msg)

                msgEnemy = await self.receive(timeout=30)
                #await asyncio.sleep(2)
                if msgEnemy.body != None:
                    naziv = msgEnemy.get_metadata("naziv")
                    self.agent.neprijatelj = naziv
                    hp = msgEnemy.get_metadata("hp")
                    damage = msgEnemy.get_metadata("damage")
                    speed = msgEnemy.get_metadata("speed")
                    print(f"\nOkruzje: {naziv} ima {hp} Hp-a, damage mu je {damage}, a brzina {speed}.\n")
                    self.agent.neprijateljHp = hp
                    self.agent.neprijateljHpMax = hp

                    msg = spade.message.Message(
                    to="bornaagent@jab.im",
                    body=("neprijatelj"),
                    metadata = {
                        "performative": "upit",
                        "ontology": "generiranje",
                        "intent" : "informacija",
                        "naziv": f"{naziv}",
                        "hp": f"{hp}",
                        "damage": f"{damage}",
                        "speed": f"{speed}"
                    })
                    await self.send(msg)

                    self.set_next_state("Drazba")

    class Drazba(State):
        async def run(self):
            msg = None
            #await asyncio.sleep(2)
            print(f"Okruzje: Mercenaryje koje možeš unajmiti su sljedeći:\n klasa (hp, damage/heal) gold\n Warrior (200, 100) 100 zlatnika\n Priest (100, 100) 70 zlatnika"+
            "\n Rogue (100, 150) 50 zlatnika\n Wizard (80, 250) 150 zlatnika")

            msgDrazba = await self.receive(timeout=30)
            #await asyncio.sleep(2)
            if msgDrazba.get_metadata("ontology") == "drazba" and msgDrazba.get_metadata("intent") == "formiranjeParty":
                self.agent.zlatoPartyaNakonDrazbe = msgDrazba.get_metadata("zlato")
                self.agent.partyGroup = msgDrazba.get_metadata("partyGroup")

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
    
    class Bitka(State):
        async def run(self):
            msg = None
            await asyncio.sleep(1)
            party = []
            if int(self.agent.brojKrugova) == 0:
                msg = spade.message.Message(
                to="bornaagent@jab.im",
                body=("partyRedPrvi"),
                )
                await self.send(msg)

                self.agent.brojKrugova = int(self.agent.brojKrugova) + 1
            
            if int(self.agent.brojKrugova) >= 1:
                msgBitkaParty = await self.receive(timeout=30)
                await asyncio.sleep(1)
                if msgBitkaParty.get_metadata("ontology") == "bitka" and msgBitkaParty.get_metadata("intent") == "RezultatParty":
                    party = msgBitkaParty.get_metadata("partyGroup")
                    sumaStete = int(msgBitkaParty.get_metadata("sumaStete"))
                    listaPretvorena = Okruzje.stringU2DArray(party)

                    enemyHp = int(self.agent.neprijateljHp) - sumaStete
                    enemyHpMax = int(self.agent.neprijateljHpMax)

                    partyStanje = ""

                    if enemyHp < 0:
                        enemyHp = 0

                    if enemyHp > 0:
                        print(f"Okruzje: Šteta koju je Party nanio je: {sumaStete}\nOkruzje: {self.agent.neprijatelj} {enemyHp} / {enemyHpMax}")
                        await asyncio.sleep(3)

                        self.agent.neprijateljHp = enemyHp

                        print("\nOkružje: Sljedeći na redu je Enemy!")

                        msg = spade.message.Message(
                        to="bornaagent2@jab.im",
                        body=("enemyRed"),
                        metadata = {
                            "performative": "rezultat",
                            "ontology": "bitka",
                            "intent" : "RezultatParty",
                            "partyGroup": f"{party}",
                        })
                        await self.send(msg)
                    

                        msgBitkaEnemy = await self.receive(timeout=30)
                        await asyncio.sleep(1)
                        if msgBitkaEnemy.get_metadata("ontology") == "bitka" and msgBitkaEnemy.get_metadata("intent") == "RezultatEnemy":
                            party = msgBitkaEnemy.get_metadata("partyGroup")
                            listaPretvorena = Okruzje.stringU2DArray(party)

                            brojOnesposobljenih = 0
                            for i in range(len(listaPretvorena)):
                                if int(listaPretvorena[i][2]) == 0:
                                    brojOnesposobljenih += 1
                                if brojOnesposobljenih == len(listaPretvorena):
                                    print(f"Okruzje: Svi party memberi su onesposobljeni, {self.agent.neprijatelj} je pobijedio!")
                                    partyStanje = "onesposobljen"
                            
                            if brojOnesposobljenih < len(listaPretvorena):
                                self.agent.brojKrugova = int(self.agent.brojKrugova) + 1
                                msg = spade.message.Message(
                                to="bornaagent@jab.im",
                                body=("partyRed"),
                                metadata = {
                                    "performative": "rezultat",
                                    "ontology": "bitka",
                                    "intent" : "RezultatParty",
                                    "partyGroup": f"{listaPretvorena}",
                                })
                                await self.send(msg)
                                self.set_next_state("Bitka")
                    
                            if brojOnesposobljenih >= len(listaPretvorena):
                                await asyncio.sleep(3)

                                print(f"Okruzje: Pobijedio je {self.agent.neprijatelj}!")

                                msg = spade.message.Message(
                                    to="bornaagent2@jab.im",
                                    body=("enemyRedGotov"),
                                    metadata = {
                                        "performative": "rezultat",
                                        "ontology": "bitka",
                                        "intent" : "RezultatParty",
                                        "rezultat": "win"
                                    })
                                await self.send(msg)
                            

                                msgParty = spade.message.Message(
                                    to="bornaagent@jab.im",
                                    body=("partyRedGotov"),
                                    metadata = {
                                        "performative": "rezultat",
                                        "ontology": "bitka",
                                        "intent" : "RezultatParty",
                                        "rezultat": "lose"

                                    })
                                await self.send(msgParty)
                                self.set_next_state("Zavrsno")

                    if enemyHp <= 0:
                        await asyncio.sleep(3)

                        print(f"Okruzje: Pobijedio je Party!")

                        msg = spade.message.Message(
                            to="bornaagent2@jab.im",
                            body=("enemyRedGotov"),
                            metadata = {
                                "performative": "rezultat",
                                "ontology": "bitka",
                                "intent" : "RezultatParty",
                                "rezultat": "lose"
                            })
                        await self.send(msg)
                    

                        msgParty = spade.message.Message(
                            to="bornaagent@jab.im",
                            body=("partyRedGotov"),
                            metadata = {
                                "performative": "rezultat",
                                "ontology": "bitka",
                                "intent" : "RezultatParty",
                                "rezultat": "win"

                            })
                        await self.send(msgParty)
                        self.set_next_state("Zavrsno")
                    
    class Zavrsno(State):
        async def run(self):
            msg = None
            await asyncio.sleep(4)
            print(f"Okruzje: Raid je završio u {self.agent.brojKrugova} krugova!")
    
    async def setup(self):
        print("Okruzje agent zapocinje")

        fsm = self.PonasanjeOkruzje()

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

        self.zlatoPartya = 0
        self.zlatoPartyaNakonDrazbe = 0
        self.partyGroup = []
        self.neprijatelj = ""
        self.neprijateljHp = ""
        self.neprijateljHpMax = ""

        self.brojKrugova = 0
        #[klasa, gold, hp, damage/heal]
        self.mercenary = [["warrior", 100, 200, 100],["priest", 70, 100, 100],["rogue", 50, 100, 150],["wizard", 150, 80, 200]]

