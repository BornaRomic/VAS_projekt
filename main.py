#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ast import parse
from queue import Empty
from re import T, X
from tkinter import SEL
from okruzje import Okruzje
from enemy import Enemy
from party import Party
import spade
import asyncio
import random
import time
import re
import string
from spade.agent import Agent
from spade.behaviour import FSMBehaviour, CyclicBehaviour, State





def main():
    okruzje = Okruzje("bornar@jab.im", "bornaromic")
    okruzje.start()
    party = Party("bornaagent@jab.im", "bornaagent")
    party.start()
    enemy = Enemy("bornaagent2@jab.im", "bornaagent2")
    enemy.start()

    

    input("Press ENTER to exit.\n")
    okruzje.stop()
    party.stop()
    enemy.stop()
    spade.quit_spade()


if __name__ == '__main__':
    main()
    