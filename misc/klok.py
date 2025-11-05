from datetime import datetime
from time import sleep
import json
import random

from rollen.algemeen import algemene_commandos
from misc.verzend import *
from misc.misc import *
from misc.berichten import *

dag = 1


@with_spelers
def klok(spelers, speler, opstarten, thema: str, *deelnemers):
    global dag
    start = True
    while True:
        witte_wolf = next((naam for naam, data in spelers.items() if data["rol"] == 'witte_wolf'), None)
        if witte_wolf:
            spelers[witte_wolf]['dag'] = int(dag)

        nu = datetime.now()
        if opstarten == 'start':
            if (nu.hour == 11 and nu.minute == 36 and nu.second == 0):
                if dag == 1 and start == False:
                    algemene_commandos.rollen(speler, *deelnemers)
                    start = True
                    genereer_startbericht('data/prompts/startbericht.txt', thema.replace('_', ' '), list(spelers))

        ## Commando's verwerken
        if nu.hour == 8 and nu.minute == 0 and nu.second == 0 and start == True:
            spelers = {name: {**data, "dood": False if data.get("dood") == -1 else data.get("dood")} for name, data in spelers.items()}
            nachtacties()
            gebeurtenissen()
        
        gearresteerd = next((naam for naam, speler in spelers.items() if speler["gearresteerd"]), None)
        if nu.hour == 13 and nu.minute == 00 and nu.second == 0 and gearresteerd:
            arrestatie()

        if nu.hour == 19 and nu.minute == 00 and nu.second == 0 and start == True:
            avondbericht()

        
        if nu.hour == 0 and nu.minute == 0 and nu.second == 1 and start == True:
            dr_frankenstein = next((naam for naam in spelers if spelers[naam]["rol"] == 'dr_frankenstein'), None)
            if dr_frankenstein:
                doden = [speler for speler in spelers if speler['huidig_dood'] == True]
                if len(doden) > 1:
                    bericht = ['Dr. Frankenstein. Je kunt gaan bouwen!\n\nDe volgende spelers zijn overleden']
                    for dode in doden:
                        bericht.append(f'{dode.capitalize()} als {spelers[dode]['rol'].replace('_', ' ')}')
                    
                    plan_bericht(spelers[dr_frankenstein]['telefoonnummer'], '\n'.join(bericht))


            monsters = [speler for speler in spelers if speler['monster'] == True]
            for monster in monsters:
                spelers[monster]['levensduur'] -= 1
                if spelers[monster]['levensduur'] == 0:
                    spelers = dood(monster, 'hoopje lichaamsdelen')
                    spelers[monster]['levensduur'] = -1
            

            piraat_slachtoffers = [speler_ for speler_ in spelers if spelers[speler_]['verdediging_toegestaan']]
            piraat = next((naam for naam in spelers if spelers[naam]["rol"] == 'piraat'), None)
            for slachtoffer in piraat_slachtoffers:
                spelers = dood(spelers, piraat, slachtoffer, 'piraat')


            dag += 1


        
        sleep(1)

@with_spelers
def gebeurtenissen(spelers):
    ## Vigilant pleegt zelfmoord
    vigilant = next((naam for naam, data in spelers.items() if data["zelfmoord"] == True), None)
    if vigilant:
        spelers = dood(vigilant, 'zelfmoord')

    ## Dokter hoort dat bescherming niet nodig was
    dokter = next((naam for naam, data in spelers.items() if data["rol"] == "dokter"), None)
    if dokter:
        if spelers[dokter]['beschermd'] == False:
            plan_bericht(spelers[dokter]['telefoonnummer'], 'Je ziet geen gevaar, waardoor je besluit weer naar huis te gaan.', zendtijd(9, 0))

    ## Cupido heeft geen koppel gemaakt
    cupido = next((naam for naam in spelers if spelers[naam]["rol"] == 'cupido'), None)
    if cupido and not spelers[cupido]['koppel_gemaakt'] and dag == 2:
        plan_bericht(spelers[cupido]['telefoonnummer'], f'Je hebt de eerste nacht geen koppel gemaakt. Je kunt nu nog slechts een koppel maken gedurende het gehele spel.')
        spelers[cupido]['koppel_gemaakt'] = 'gemist'



@with_spelers
@staticmethod
def arrestatie(spelers):
    gearresteerd = next((naam for naam, speler in spelers.items() if speler["gearresteerd"]), None)
    stemmen = spelers[gearresteerd][stemmen]
    if stemmen <= 0:
        plan_bericht(naam_nummer('dorp_app'), f'{gearresteerd.capitalize()} is vrijgelaten!')
    else:
        spelers[gearresteerd]['dood'] = True
        plan_bericht(naam_nummer('dorp_app'), f"{gearresteerd.capitalize()} is schuldig bevonden. {gearresteerd.capitalize()} was {spelers[gearresteerd]['rol']}")

        ## Reset stemmen
        for speler in spelers.values():
            speler['gestemd'] = None
            speler['stemmen'] = 0






def nachtacties():
    algemene_commandos.verwerken('bart')
    plan_bericht(naam_nummer('dorp_app'), ochtendbericht(), zendtijd(9, 0))

@with_spelers
def ochtendbericht(spelers):

    for speler_ in spelers:
        spelers[speler_]['stuntman_dood'] = False
        if spelers[speler_]['rol'] == 'welp' and dag == 4:
            spelers[speler]['rol'] == 'weerwolf'

    doden = [speler_ for speler_ in spelers if spelers[speler_]['huidig_dood']]
    tot_leven_gewekt = [speler_ for speler_ in spelers if spelers[speler_]['tot_leven_gewekt']]

    for dode in doden:
        spelers[dode]['stuntman_dood'] = True

    ## Reset nachtacties
    for speler in spelers:
        spelers[speler]['tijdelijke_rol'] = None
        spelers[speler]['tijdelijke_aura'] = None
        spelers[speler]['locatie'] = speler if not spelers[speler]['rol'] == 'slaaf' else 'schuur'
        spelers[speler]['gasten'] = []
        spelers[speler]['gearresteerd'] = False
        spelers[speler]['nachtactie'] = None
        spelers[speler]['gespiekt'] = False
        spelers[speler]['lijfwacht_bescherming'] = None
        spelers[speler]['cooldown'] -= 1
        spelers[speler]['dag'] = dag


    if len(doden) == 0:
        return f'Er is vannacht niemand overleden.'
    else:
        berichten = []
        for dode in doden:
            bericht = f"{dode.capitalize()} was {spelers[dode]['rol']}. Er is een {spelers[dode]['doodsoorzaak']} gevonden."
            berichten.append(bericht)
        
        for monster in tot_leven_gewekt:
            bericht = f"{monster.capitalize()} is weer tot leven gewekt."
            spelers[monster]['tot_leven_gewekt'] = False
            berichten.append(bericht)

        gearresteerd = next((naam for naam, speler in spelers.items() if speler["gearresteerd"]), None)
        if gearresteerd:
            berichten.append(f'\n{spelers[gearresteerd].capitalize()} is gearresteerd. Jullie mogen tot 13:00 stemmen over zijn/haar lot.')

        berichten = "\n".join(berichten)
        ochtenbericht_tekst = f'De volgende mensen zijn vannacht overleden:\n{berichten}'

        return ochtenbericht_tekst


@with_spelers
def avondbericht(spelers):

    ## Reset stuntman doden
    for speler_ in spelers:
        spelers[speler_]['stuntman_dood'] = False

    with open('dit_is_een_test.txt', 'w') as file:
        file.write('hi')
    if dag == 1:
        ## Berekent het maximaal aantal stemmen op een persoon
        meeste_stemmen = max(spelers[speler_]["stemmen"] for speler_ in spelers)
        gedeelde_stemmen = [naam for naam, speler in spelers.items() if speler["stemmen"] == meeste_stemmen]

        ## Niks gebeurt wanneer niemand heeft gestemd
        if all(spelers[speler_]['stemmen'] == 0 for speler_ in spelers):
            burgemeester = random.choice(spelers)
            plan_bericht(naam_nummer('dorp_app'), f'Er is niet gestemd, dus het universum heeft besloten dat {burgemeester.capitalize()} de nieuwe burgemeester is!')

        ## Als het een gelijk spel is
        if len(gedeelde_stemmen) > 1:
            burgemeester = random.choice(meeste_stemmen)
            spelers[burgemeester]['burgemeester'] = True
            plan_bericht(naam_nummer('dorp_app'), f'Het is een gelijk spel, dus het universum heeft besloten dat {burgemeester.capitalize()} de nieuwe burgemeester is!')
        
        else:
            burgemeester = gedeelde_stemmen[0]
            spelers[burgemeester]['burgemeester'] = True
            plan_bericht(naam_nummer('dorp_app'), f'Het volk heeft besloten. {burgemeester.capitalize()} is de nieuwe burgemeester!')

        ## Reset stemmen
        for speler in spelers.values():
            speler['gestemd'] = None
            speler['stemmen'] = 0


    else:
        ## Niks gebeurt wanneer niemand heeft gestemd
        if all(speler['stemmen'] == 0 for speler in spelers):
            return f'Er is niemand geëxecuteerd.'


        ## Berekent het maximaal aantal stemmen op een persoon

        dictatorwolf = next((naam for naam in spelers if spelers[naam]["stemming_ingezet"] == 'dictatorwolf'), None)
        if dictatorwolf:
            meeste_stemmen = max(speler["stemmen"] for speler in spelers.values() if speler['stemmen'] > 500)
        else:
            meeste_stemmen = max(speler["stemmen"] for speler in spelers.values())

        ## Berekent welke spelers het maximale aantal stemmen hebben
        gedeelde_stemmen = [naam for naam, speler in spelers.items() if speler["stemmen"] == meeste_stemmen]

        ## Bepaalt wie momenteel burgemeester is
        burgemeester = next((naam for naam in spelers if spelers[naam]["burgemeester"]), None)

        bericht = None

        ## Als het een gelijk spel is
        if len(gedeelde_stemmen) > 1:
            ## Als de burgemeester heeft gestemd op een persoon met de meeste stemmen is dit doorslaggevend
            if spelers[burgemeester]['gestemd'] in gedeelde_stemmen:
                slachtoffer = spelers[burgemeester]['gestemd'].capitalize()
                spelers[slachtoffer.lower()]['dood'] = True
                spelers[slachtoffer.lower()]['stuntman_dood'] = True
                bericht = f"{slachtoffer} is geëxecuteerd. {slachtoffer} was {spelers[slachtoffer]['rol'].replace('_', ' ')}"
            ## Als de burgemeester niet heeft gestemd op de persoon met de meeste stemmen
            else:
                plan_bericht(spelers[burgemeester]['telefoonnummer'], 'Tijdens de executie was het gelijkspel. Jij mag nu aanwijzen wie er geëxecuteerd wordt. Dit doe je met /doorslag <naam>')
                spelers[burgemeester]['executie_toegestaan'] = True
                bericht = f'De executie is geëindigd in een gelijkspel. De burgemeester ({burgemeester.capitalize()}) mag nu bepalen wie er geëxecuteerd wordt.'
        
        ## Als het geen gelijkspel is
        else:
            slachtoffer = gedeelde_stemmen[0].capitalize()
            if spelers[slachtoffer.lower()]['beschermende_wolf']:
                plan_bericht(spelers[spelers[slachtoffer.lower()]['beschermende_wolf']]['telefoonnummer'], 'Je hebt je kracht succesvol ingezet!')
                spelers[spelers[slachtoffer.lower()]['beschermende_wolf']]['kracht_ingezet'] = True
                bericht = f"{slachtoffer} kijkt even rond, en loopt daarna ongedeerd weg."
    
            else:
                spelers[slachtoffer.lower()]['dood'] = True
                spelers[slachtoffer.lower()]['stuntman_dood'] = True
                bericht = f"{slachtoffer} is geëxecuteerd. {slachtoffer} was {spelers[slachtoffer]['rol'].replace('_', ' ')}"
        
        ## Reset stemmen
        for speler in spelers:
            speler['gestemd'] = None
            speler['stemmen'] = 0

        eigen_rechter = next((naam for naam in spelers if spelers[naam]["stemming_ingezet"] == 'eigen_rechter'), None)
        if eigen_rechter:
            bericht = f'{eigen_rechter.capitalize()} stapt naar voren en besluit dat {slachtoffer.capitalize()} de dood verdient.\n\n{bericht}'
            spelers[eigen_rechter]['stemming_beinvloed'] = False

        dictatorwolf = next((naam for naam in spelers if spelers[naam]["stemming_ingezet"] == 'dictatorwolf'), None)
        if dictatorwolf:
            spelers[eigen_rechter]['stemming_beinvloed'] = False
        
        plan_bericht(naam_nummer('dorp_app'), bericht)