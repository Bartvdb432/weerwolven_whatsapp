import random
import pickle
import pandas as pd
import random
import yaml
import re
import requests
import threading
from collections import Counter
from collections import defaultdict

from rollen.rollen import rol as rol_class
from misc.misc import *
from misc.verzend import *
from misc.feedback import basis_feedback




class algemene_commandos:
    @staticmethod
    @with_spelers
    def info(spelers, speler, informatie):
        with open('data/beschrijvingen.yaml', 'r') as file:
            beschrijvingen = yaml.safe_load(file)
        if informatie == 'algemeen':
            plan_bericht(spelers[speler]['telefoonnummer'], beschrijvingen['algemeen'])
        elif informatie == 'rol':
            plan_bericht(spelers[speler]['telefoonnummer'], beschrijvingen[spelers[speler]['rol']])
    
    @staticmethod
    @with_commandos
    def reset(commandos, speler, commando):
        target = f"{commando}_verwerken"
        if not any(entry["speler"] == speler and entry["commando"] == target for entry in commandos):
            return f'Je hebt dit commando niet uitgevoerd.'
        commandos[:] = [entry for entry in commandos if not (entry["speler"] == speler and entry["commando"] == target)]

        ## Stuurt speler terug naar huis
        with open('data/spelers.json', 'r') as file:
            spelers = json.load(file)
        
        spelers[speler]['op_straat'] = False

        with open('data/spelers.json', 'w') as file:
            json.dump(spelers, file, indent = 4)

        return f'Commando verwijderd.'

    @with_spelers
    @staticmethod
    def dobbel(spelers, speler, **kwargs):
        group_id = kwargs.get("group_id")
        group_specific_id = kwargs.get("group_specific_id")

        getallen_dict = {
            1: (
                "⬜⬜⬜⬜⬜⬜⬜\n"
                "⬜⬜⬜⬜⬜⬜⬜\n"
                "⬜⬜⬜⬜⬜⬜⬜\n"
                "⬜⬜⬜⬛⬜⬜⬜\n"
                "⬜⬜⬜⬜⬜⬜⬜\n"
                "⬜⬜⬜⬜⬜⬜⬜\n"
                "⬜⬜⬜⬜⬜⬜⬜"
            ),
            2: (
                "⬜⬜⬜⬜⬜⬜⬜\n"
                "⬜⬜⬜⬜⬜⬛⬜\n"
                "⬜⬜⬜⬜⬜⬜⬜\n"
                "⬜⬜⬜⬜⬜⬜⬜\n"
                "⬜⬜⬜⬜⬜⬜⬜\n"
                "⬜⬛⬜⬜⬜⬜⬜\n"
                "⬜⬜⬜⬜⬜⬜⬜"
            ),
            3: (
                "⬜⬜⬜⬜⬜⬜⬜\n"
                "⬜⬜⬜⬜⬜⬛⬜\n"
                "⬜⬜⬜⬜⬜⬜⬜\n"
                "⬜⬜⬜⬛⬜⬜⬜\n"
                "⬜⬜⬜⬜⬜⬜⬜\n"
                "⬜⬛⬜⬜⬜⬜⬜\n"
                "⬜⬜⬜⬜⬜⬜⬜"
            ),
            4: (
                "⬜⬜⬜⬜⬜⬜⬜\n"
                "⬜⬛⬜⬜⬜⬛⬜\n"
                "⬜⬜⬜⬜⬜⬜⬜\n"
                "⬜⬜⬜⬜⬜⬜⬜\n"
                "⬜⬜⬜⬜⬜⬜⬜\n"
                "⬜⬛⬜⬜⬜⬛⬜\n"
                "⬜⬜⬜⬜⬜⬜⬜"
            ),
            5: (
                "⬜⬜⬜⬜⬜⬜⬜\n"
                "⬜⬛⬜⬜⬜⬛⬜\n"
                "⬜⬜⬜⬜⬜⬜⬜\n"
                "⬜⬜⬜⬛⬜⬜⬜\n"
                "⬜⬜⬜⬜⬜⬜⬜\n"
                "⬜⬛⬜⬜⬜⬛⬜\n"
                "⬜⬜⬜⬜⬜⬜⬜"
            ),
            6: (
                "⬜⬜⬜⬜⬜⬜⬜\n"
                "⬜⬛⬜⬜⬜⬛⬜\n"
                "⬜⬜⬜⬜⬜⬜⬜\n"
                "⬜⬛⬜⬜⬜⬛⬜\n"
                "⬜⬜⬜⬜⬜⬜⬜\n"
                "⬜⬛⬜⬜⬜⬛⬜\n"
                "⬜⬜⬜⬜⬜⬜⬜"
            ),
            
        }


        getallen = [random.randint(1, 6) for x in range(2)]
        bak = 0
        bak += sum([1 for getal in getallen if getal == 6])
        if len(list(set(getallen))) == 1:
            bak += 1
        if sum(getallen) == 6:
            bak += 1

        if bak == 0:
            bakken = 'Je hoeft geen bakken te trekken.'
        if bak == 1:
            bakken = 'Trek een bak!'
        if bak == 2:
            bakken = 'Trek twee bakken!'
        if bak == 3:
            bakken = 'Trek drie bakken!'
        bericht = f"@{spelers[speler]['telefoonnummer']}\n\n{getallen_dict[getallen[0]]}\n\n{getallen_dict[getallen[1]]}\n\n" + bakken

        if group_id is None:
            return bericht
        
        elif group_id is not None:
            plan_bericht(group_id, bericht, mentions = [speler])
            return None
        
    @staticmethod
    @with_spelers
    def radje(spelers, speler, *args, **kwargs):
        if len(args) < 1:
            args = [speler_ for speler_ in spelers if not spelers[speler_]['dood']]
        group_id = kwargs.get("group_id")
        group_specific_id = kwargs.get("group_specific_id")

        doelwit = random.choice(list(args))

        if group_id is None:
            return f'Het heilige radje heeft gekozen: {doelwit.capitalize()}'
        
        elif group_id is not None:
            plan_bericht(group_id, f'@{spelers[speler]["telefoonnummer"]} Het heilige radje heeft gekozen: {doelwit.capitalize()}', mentions = [speler])
            return None

    
    @staticmethod
    @with_commandos
    def acties(commandos, speler):
        commandos[:] = [entry for entry in commandos if (entry["speler"] == speler)]
        if len(commandos) == 0:
            return f'Je hebt geen acties uitgevoerd.'
        joined = "\n".join(f'/{commando["commando"]}' for commando in commandos)
        return f'Je hebt {"de volgende commandos" if len(commandos) > 1 else "het volgende commando"} uitgevoerd:\n{joined}'

    @with_spelers
    @staticmethod
    def help(spelers, speler, probleem):
        tekst = f'{speler.capitalize()} heeft een probleem en wil graag geholpen worden:\n{probleem}'
        requests.post("https://ntfy.sh/weerwolven_whatsapp_bartvdb432",
            data = tekst,
            headers={ "Priority": "3",
                     "Title": f"{speler.capitalize()} vraagt om hulp."})
    

    @with_spelers
    @staticmethod
    def opvolger(spelers, speler, opvolger):
        if not (spelers[speler]['burgemeester'] and spelers[speler]['dood']):
            return f'Je kunt geen opvolger aanwijzen.'
        spelers[opvolger]['burgemeester'] = True
        spelers[speler]['burgemeester'] = False
        plan_bericht(naam_nummer('dorp_app'), f'{opvolger.capitalize()} is de nieuwe burgemeester!')
    
    @with_spelers
    @staticmethod
    def doorslag(spelers, speler, doelwit):
        burgemeester = next((naam for naam in spelers if spelers[naam]["burgemeester"]), None)
        if speler != burgemeester:
            return f'Je bent geen burgemeester.'
        if not spelers[speler]['executie_toegestaan']:
            return f'Dit is niet het moment om de doorslag te geven bij een executie'
        
        if spelers[doelwit]['beschermende_wolf']:
            spelers[spelers[doelwit]['beschermende_wolf']]['kracht_ingezet'] = True
            plan_bericht(spelers[spelers[doelwit]['beschermende_wolf']]['telefoonnummer'], 'Je hebt je kracht succesvol ingezet!')
            spelers[spelers[doelwit]['beschermende_wolf']]['kracht_ingezet'] = True
            bericht = f"{doelwit.capitalize()} kijkt even rond, en loopt daarna ongedeerd weg."

        spelers[doelwit]['dood'] = True
        spelers[burgemeester]['executie_toegestaan'] = False
        plan_bericht(naam_nummer('dorp_app'), f"{doelwit} is geëxecuteerd. {doelwit} was {spelers[doelwit]['rol'].replace('_', ' ')}")
        with open('data/commandos.json', 'r') as file:
            commandos = json.load(file)
        
        commandos = [commando for commando in commandos if commando['speler'] == doelwit]

        with open('data/commandos.json', 'w') as file:
            json.dump(commandos, file, indent = 4)
    
    @staticmethod
    @with_spelers
    def verdedig(spelers, speler, verdediging):
        piraat = next((naam for naam, speler in spelers.items() if speler["rol"] == 'piraat'), None)
        feedback = basis_feedback(spelers, speler, [], 'nacht')
        if not feedback:
            if verdediging not in ['opzij', 'maliënkolder', 'achteruit']:
                return f'Deze verdediging is niet geldig. Kies uit opzij, maliënkolder of achteruit.'
            verdediging_map = {
                'kromzwaard': 'opzij',
                'rapier': 'maliënkolder',
                'pistool': 'achteruit'
            }

            toegestaan = spelers[speler]['verdediging_toegestaan']

            if verdediging_map.get(toegestaan) == verdediging:
                spelers = dood(spelers, speler, speler, 'piraat')
                plan_bericht(spelers[piraat]['telefoonnummer'], 'Je hebt het duel gewonnen!')
                spelers[speler]['verdediging_toegestaan'] = False

            else:
                plan_bericht(spelers[piraat]['telefoonnummer'], 'Je hebt het duel verloren.')
                spelers[speler]['verdediging_toegestaan'] = False

    @staticmethod
    @with_spelers
    def zwaard(spelers, speler, doelwit):
        feedback = basis_feedback(spelers, speler, ['zwaard'], 'avond', doelwit)
        if not feedback:
            if spelers[speler]['zwaard'] <= 0:
                return f'Je hebt geen zwaard.'
            verwerk_commando(spelers, speler, 'zwaard_verwerken', doelwit)
    
    @staticmethod
    @with_spelers
    def stem(spelers, speler, kandidaat, **kwargs):
        group_id = kwargs.get("group_id")
        group_specific_id = kwargs.get("group_specific_id")

        # Wrong group
        if group_id != naam_nummer('stem_app') and group_id is None:
            return f'Stemmen doe je in de stem app.'
        
        elif group_id != naam_nummer('stem_app') and group_id is not None:
            plan_bericht(group_id, f'@{spelers[speler]["telefoonnummer"]} stemmen doe je in de stem app.', mentions = [speler])
            return None

        gearresteerd = next((naam for naam, speler in spelers.items() if speler["gearresteerd"]), None)
        if gearresteerd:
            dagdelen, tijd = dagdeel('agent')
            if spelers[speler]['dood']:
                plan_bericht(spelers[speler]['telefoonnummer'], 'Je bent al dood.')
            if 'agent' not in dagdelen:
                return f'Je kunt deze actie alleen uitvoeren tussen {" en ".join(tijd)} of 16:00 en 19:00.'
            if kandidaat not in ['schuldig', 'onschuldig']:
                return {'react': '❌'}
            if spelers[speler]['gestemd']:
                spelers[gearresteerd]['stemmen'] -= spelers[speler]['gestemd']

            if kandidaat == 'schuldig':
                spelers[gearresteerd]['stemmen'] += 1
                spelers[speler]['gestemd'] = 1
            if kandidaat == 'onschuldig':
                spelers[gearresteerd]['stemmen'] -= 1
                spelers[speler]['gestemd'] = -1
            
        else:
            feedback = basis_feedback(spelers, speler, ['stem'], 'altijd', kandidaat)
            dagdelen, tijd = dagdeel('stemmen')
            if 'stemmen' not in dagdelen:
                return f'Je kunt deze actie alleen uitvoeren tussen {" en ".join(tijd)}.'
            
            # Vote not allowed
            if feedback:
                return feedback

            if spelers[speler]['gestemd']:
                spelers[spelers[speler]['gestemd']]['stemmen'] += -1

            # Vote successful
            spelers[kandidaat]['stemmen'] += 1
            spelers[speler]['gestemd'] = kandidaat
            return {"react": "✅"}
    

    @with_spelers
    @staticmethod
    def stemmen(spelers, speler, arg, **kwargs):
        group_id = kwargs.get("group_id")
        group_specific_id = kwargs.get("group_specific_id")
        feedback = basis_feedback(spelers, speler, [], 'stemmen')
        if not feedback:
            if arg == 'aantal':
                stemmen = [spelers[speler_]['gestemd'] for speler_ in spelers if spelers[speler_]['gestemd']]
                counts = Counter(stemmen)
                bericht = f'De huidige tussenstand luidt als volgt:\n\n' + '\n'.join(f'{speler_.capitalize()}: {aantal}' for speler_, aantal in counts.most_common())

                if group_id is None:
                    return bericht
                
                elif group_id is not None:
                    plan_bericht(group_id, bericht, mentions = [speler])
                    return None
            if arg == 'spelers':
                stemmen = [spelers[speler_]['gestemd'] for speler_ in spelers if spelers[speler_]['gestemd']]

                # Count votes
                counts = Counter(stemmen)

                # Collect who voted for whom
                voters_per_speler = defaultdict(list)
                for voter, data in spelers.items():
                    gestemd = data.get('gestemd')
                    if gestemd:
                        voters_per_speler[gestemd].append(voter.capitalize())

                # Build message
                bericht = "De huidige tussenstand luidt als volgt:\n\n"
                for speler_, aantal in counts.most_common():
                    stemmers = ', '.join(voters_per_speler[speler_])
                    bericht += f"{speler_.capitalize()}: {stemmers}\n"
                
                if group_id is None:
                    return bericht
                
                elif group_id is not None:
                    plan_bericht(group_id, bericht, mentions = [speler])
                    return None
            else:
                return f'Gebruik /stemmen als volgt: /stemmen <aantal/spelers>'
            

        else:
            return feedback



    @with_spelers
    @staticmethod
    def antwoorden(spelers, speler, antwoord):
        if 'cipier' not in spelers[speler]['locatie']:
            return f'Je bent niet gevangen genomen, dus je kunt dit commando nu niet gebruiken.'
        cipier = spelers[speler]['locatie'].split('_')[0]
        plan_bericht(spelers[cipier]['telefoonnummer'], antwoord)