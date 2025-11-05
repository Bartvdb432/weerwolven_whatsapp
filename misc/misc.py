import pandas as pd
from functools import wraps
import pickle
import json
from datetime import datetime, time
import inspect
import types
import os
from functools import wraps
import Levenshtein
import ast
import random

from misc.verzend import *

def naam_nummer(naam):
    dataframe = pd.read_csv('data/telefoonboek.csv')
    nummer = dataframe.loc[dataframe["naam"] == naam.lower(), "nummer"].values[0]
    return nummer

def nummer_naam(nummer):
    dataframe = pd.read_csv('data/telefoonboek.csv')
    test
    naam = dataframe.loc[dataframe["nummer"] == nummer.lower(), "naam"].values[0]
    return naam


def with_spelers(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        ## Opent speler json
        with open('data/spelers.json', 'r', encoding='utf-8') as file:
            spelers = json.load(file)
        
        ## Runt functie
        result = function(spelers, *args, **kwargs)

        ## Slaat spelers op
        with open('data/spelers.json', 'w', encoding='utf-8') as file:
            json.dump(spelers, file, indent=4)

        ## Stuurt feedback terug
        return result

    return wrapper



def with_commandos(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        ## Opent speler json
        with open('data/commandos.json', 'r', encoding='utf-8') as file:
            commandos = json.load(file)
        
        ## Runt functie
        result = function(commandos, *args, **kwargs)

        ## Slaat spelers op
        with open('data/commandos.json', 'w', encoding='utf-8') as file:
            json.dump(commandos, file, indent=4)

        ## Stuurt feedback terug
        return result

    return wrapper



def verwerk_commando(spelers, speler, cmd, *args):
    with open('data/commandos.json', 'r') as file:
        commandos: list = json.load(file)
    
    commandos.append({
        'speler': speler,
        'telefoonnummer': spelers[speler]['telefoonnummer'],
        'commando': cmd,
        'argumenten': args if args else [],
        'tijd': str(datetime.now())
    })

    with open('data/commandos.json', 'w') as file:
        json.dump(commandos, file, indent = 4)



def spelling(input_commando, bestaande_commandos):
    best_match = min(bestaande_commandos, key=lambda cmd: Levenshtein.distance(input_commando, cmd))
    if Levenshtein.distance(input_commando, best_match) <= 2:  # tolerance for typos
        return f"Onbekend commando. Bedoelde je misschien /{best_match}?"
    return "Onbekend commando."



import inspect

def argumenten(func, args):
    nummers = {0: 'geen', 1: 'één', 2: 'twee', 3: 'drie', 4: 'vier', 5: 'vijf'}

    sig = inspect.signature(func)
    params = list(sig.parameters.values())[2:]  # skip spelers, speler

    # Count required and total positional args
    required_count = sum(
        1 for p in params
        if p.default == inspect.Parameter.empty
        and p.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
    )
    total_count = sum(
        1 for p in params
        if p.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
    )

    has_varargs = any(p.kind == inspect.Parameter.VAR_POSITIONAL for p in params)
    given = len(args)

    # ✅ allow range between required and total
    if has_varargs:
        if given < required_count:
            return f"Dit commando accepteert minimaal {nummers[required_count]} {'argument' if required_count == 1 else 'argumenten'}."
    else:
        if not (required_count <= given <= total_count):
            if required_count == total_count:
                # all required
                return f"Dit commando accepteert precies {nummers[required_count]} {'argument' if required_count == 1 else 'argumenten'}."
            elif given < required_count:
                return f"Dit commando accepteert minimaal {nummers[required_count]} {'argument' if required_count == 1 else 'argumenten'}."
            else:
                return f"Dit commando accepteert maximaal {nummers[total_count]} {'argument' if total_count == 1 else 'argumenten'}."



def dagdeel(tijdstip):
    dagdelen = ['altijd']
    now = datetime.now().time()

    tijdstippen = {
        'agent':    ('9:00', '13:00'),
        'ochtend':  ('9:00', '16:00'),
        'stemmen':  ('16:00', '19:00'),
        'avond':    ('19:00', '22:00'),
        'nacht':    ('22:00', '0:00'),
        'slapen':   ('00:00', '9:00'),
        'stiekeme_kind': ('9:00', '19:30'),
        'priester': ('9:00', '19:00'),
        'dr_frankenstein': ('24:00', '11:00'),
        'stuntman': ('9:00', '22:00'),
        'altijd':   ('00:00', '23:59'),
    }

    if time(9, 0, 0) <= now < time(13, 0, 0):
        dagdelen.append('agent')
    if time(9, 0, 0) <= now < time(16, 0, 0):
        dagdelen.append('ochtend')
    if time(16, 0, 0) <= now < time(19, 0, 0):
        dagdelen.append('stemmen')
    if time(19, 0, 0) <= now < time(22, 0, 0):
        dagdelen.append('avond')
    if time(22, 0, 0) <= now < time(23, 59, 59):
        dagdelen.append('nacht')
    if now >= time(23, 59, 59) or now < time(9, 0, 0):
        dagdelen.append('slapen')
    if time(9, 0, 0) <= now < time(19, 30, 0):
        dagdelen.append('stiekeme_kind')
    if time(9, 0, 0) <= now < time(19, 0, 0):
        dagdelen.append('priester')
    if time(0, 0, 1) <= now < time(11, 0, 0):
        dagdelen.append('dr_frankenstein')
    if time(9, 0, 0) <= now < time(22, 0, 0):
        dagdelen.append('stuntman')

    #########################################################################################################################
    dagdelen.extend(['agent', 'ochtend', 'stemmen', 'avond', 'nacht', 'slapen', 'stiekeme_kind', 'priester', 'dr_frankenstein', 'stuntman'])
    return dagdelen, tijdstippen[tijdstip]



def test(bericht: str = 'Test'):
    with open('test.txt', 'w') as file:
        file.write(bericht)


def dood(spelers, speler, doelwit, reden):
    ## Als de speler beschermd wordt door de lijfwacht
    if spelers[doelwit]['lijfwacht_bescherming']:
        if spelers[spelers[doelwit]['lijfwacht_bescherming']]['lijfwacht'] > 1:
            spelers[spelers[doelwit]['lijfwacht_bescherming']]['lijfwacht'] += -1
            plan_bericht(spelers[spelers[doelwit]['lijfwacht_bescherming']]['telefoonnummer'], 'Je hebt je doelwit met succes beschermd.', zendtijd(9, 0))
            return spelers
        else:
            test(spelers[doelwit]['lijfwacht_bescherming'])
            spelers = dood(spelers, speler, spelers[doelwit]['lijfwacht_bescherming'], reden)
            return spelers

    ## Als de speler beschermd wordt door de dokter
    if spelers[doelwit]['dokter_bescherming']:
        spelers[spelers[doelwit]['dokter_bescherming']]['spuiten'] += -1
        if not spelers[doelwit]['spiegelwolf']:
            spelers[spelers[doelwit]['dokter_bescherming']]['beschermd'] = True
        return spelers

    if spelers[speler]['rol'] == 'vigilant' and spelers[doelwit]['bondgenootschap'] == 'burgers':
        spelers[speler]['zelfmoord'] = True
    
    ## Als de speler bezocht wordt door de hoer
    for gast in spelers[doelwit]['gasten']:
        if spelers[gast]['rol'] == 'hoer':
            spelers = dood(spelers, speler, gast, reden)
    

    if spelers[doelwit]['rol'] == 'slavendrijver':
        slaven = [speler_ for speler_ in spelers if spelers[speler_]['rol'] == 'slaaf' and not spelers[speler_]['dood']]
        if len(slaven) >= 2:
            spelers = dood(spelers, speler, random.choice(slaven), reden)
            return spelers


    ## Markeert de speler als dood
    spelers[doelwit]['dood'] = True

    ## Voegt speler toe aan beide doden lijsten
    spelers[doelwit]['dood'] = True
    spelers[doelwit]['huidig_dood'] = True
    spelers[doelwit]['doodsoorzaak'] = reden

    spelers[speler]['slachtoffers'] += 1

    return spelers


def converteer_string(s):
    if not isinstance(s, str):
        return s

    s_strip = s.strip()

    if s_strip.lower() == 'none':
        return None
    
    if s_strip.lower() == 'true':
        return True
    if s_strip.lower() == 'false':
        return False

    if s_strip.isdigit() or (s_strip.startswith('-') and s_strip[1:].isdigit()):
        return int(s_strip)

    if (s_strip.startswith('[') and s_strip.endswith(']')) or (s_strip.startswith('{') and s_strip.endswith('}')):
        try:
            value = ast.literal_eval(s_strip)
            return value
        except (ValueError, SyntaxError):
            pass

    return s