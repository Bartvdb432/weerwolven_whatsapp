import re
import random
import datetime

from misc.misc import *
from misc.feedback import *
from misc.verzend import *
from misc.berichten import *


class rol:
    pass

class ijzersmid(rol):
    rol =               'ijzersmid'
    aura =              'goed'
    bondgenootschap =   'burgers'
    nachtimmuun =       False
    @with_spelers
    @staticmethod
    def maken(spelers, speler):
        """Registreert het maken van een schild of zwaard als dit mogelijk is en geeft feedback.

        Args:
            (spelers) (dict): Alle spelers en hun gegevens.
            speler (str): Naam van speler die het commando uitvoert.

        Returns:
            str: Feedback die naar de speler wordt gestuurd.
        """

        ## Genereert algemene feedback
        feedback = basis_feedback(spelers, speler, ['maken', 'geven'], 'avond')
        if not feedback:

            ## Checkt of de speler al een voorwerp heeft gemaakt
            if spelers[speler]['voorwerp']:
                return f'Je hebt al een {spelers[speler]["voorwerp"]}. Geef dit eerst weg met /geven <naam>.'
            
            ## Zet het commando in de wacht
            verwerk_commando(spelers, speler, 'maken_verwerken')

            ## Geeft feedback
            return 'Check!'
        
        ## Geeft algemene feedback
        else:
            return feedback

    @with_spelers
    @staticmethod
    def maken_verwerken(spelers, speler, *args):
        """Verwerkt het commando maken van de ijzersmid. Geeft de speler het schild of zwaard.

        Args:
            (spelers) (dict): Alle spelers en hun gegevens.
            speler (str): Naam van speler die het commando uitvoert.
        """

        ## Verandert het te maken voorwerp
        spelers[speler]['huidig_voorwerp'] = 'schild' if spelers[speler]['huidig_voorwerp'] != 'schild' else 'zwaard'

        ## Geeft de speler het voorwerp om weg te geven
        spelers[speler]['voorwerp'] = spelers[speler]['huidig_voorwerp']

    @with_spelers
    @staticmethod
    def geven(spelers, speler, ontvanger):
        """Registreert het maken van een schild of zwaard als dit mogelijk is en geeft feedback.

        Args:
            (spelers) (dict): Alle spelers en hun gegevens.
            speler (str): Naam van speler die het commando uitvoert.
            ontvanger (str): Naam van de ontvanger van het voorwerp.

        Returns:
            str: Feedback die naar de speler wordt gestuurd.
        """

        ## Genereert algemene feedback
        feedback = basis_feedback(spelers, speler, ['maken', 'geven'], 'avond', ontvanger)
        if not feedback:
            ## Checkt of de speler wel een voorwerp heeft om weg te geven
            if not spelers[speler]['voorwerp']:
                return f'Je hebt nog geen voorwerp om weg te geven. Maak dit eerst met /maken.'
            
            ## Zet het commando in de wacht
            verwerk_commando(spelers, speler, 'geven_verwerken', ontvanger)

            ## Geeft feedback
            return 'Check!'
        
        ## Geeft algemene feedback
        else:
            return feedback

    @with_spelers
    @staticmethod
    def geven_verwerken(spelers, speler, *args):
        """Verwerkt het commando geven van de ijzersmid. Geeft de ontvanger het schild of zwaard.

        Args:
            (spelers) (dict): Alle spelers en hun gegevens.
            speler (str): Naam van de speler die het commando uitvoert.
            args (str): Naam van de ontvanger van het voorwerp.
        """

        ## Bepaald de ontvanger en het te ontvangen voorwerp
        ontvanger = args[0] if not spelers[args[0]]['robbie_rotten'] else spelers[args[0]]['robbie_rotten']
        voorwerp = spelers[speler]['voorwerp']

        ## Geeft ontvanger het voorwerp
        spelers[ontvanger][voorwerp] += 1
        plan_bericht(spelers[ontvanger]['telefoonnummer'], f'_Je hebt een *{voorwerp}* gekregen!_', zendtijd(9, 0))

        ## Haalt voorwerp weg bij speler
        spelers[speler]['voorwerp'] = None

        ## Stuurt de ijzersmid de straat op
        spelers[speler]['locatie'] = 'straat'
        spelers[speler]['op_straat'] = True

        ## Verwisselt het voorwerp
        spelers[speler]['huidig_voorwerp'] = 'zwaard' if spelers[speler]['huidig_voorwerp'] == 'schild' else 'schild'

    @with_spelers
    @staticmethod
    def inventaris(spelers, speler):
        """Vertelt de ijzersmid welk voorwerp hij/zij op het moment weg kan geven.

        Args:
            (spelers) (dict): Alle spelers en hun gegevens.
            speler (str): Naam van de speler die het commando uitvoert.

        Returns:
            str: Feedback van welk item de speler heeft
        """

        ## Vertelt de speler dat hij/zij een schild/zwaard heeft
        if spelers[speler]['voorwerp']:
            return f'Je hebt momenteel een {spelers[speler]["voorwerp"]} om weg te geven.'
        
        ## Vertelt de speler dat hij/zij niks heeft
        else:
            return f'Je hebt momenteel niks om weg te geven.'



class blocker(rol):
    rol =               'blocker'
    aura =              'goed'
    bondgenootschap =   'burgers'
    nachtimmuun =       False
    @with_spelers
    @staticmethod
    def blokkeer(spelers, speler, doelwit):
        """Registreert het blokkeren van een speler als dit mogelijk is en geeft feedback.

        Args:
            (spelers) (dict): Alle spelers en hun gegevens.
            speler (str): Naam van de speler die het commando uitvoert.
            doelwit (str): Naam van het doelwit van de blokkade.

        Returns:
            str: Feedback die naar de speler wordt gestuurd.
        """

        ## Genereert algemene feedback
        feedback = basis_feedback(spelers, speler, ['blokkeer'], 'avond', doelwit)
        if not feedback:

            ## Vertelt de speler dat hij/zij zichzelf niet kan blokkeren
            if speler == doelwit:
                return f'Je kunt jezelf niet blokkeren.'
            
            ## Vertelt de speler dat het doelwit niet twee keer achter elkaar dezelfde persoon mag zijn
            if doelwit == spelers[speler]['doelwit']:
                return f'Je kunt niet twee keer achter elkaar dezelfde persoon blokkeren.'
            
            ## Zet het commando in de wacht
            verwerk_commando(spelers, speler, 'blokkeer_verwerken', doelwit)

            ## Geeft feedback
            return 'Check!'
        
        ## Geeft algemene feedback
        else:
            return feedback
    
    @with_spelers
    @staticmethod
    def blokkeer_verwerken(spelers, speler, *args):
        """Verwerkt het commando blokkeer van de blocker. Blokkeert het doelwit, tenzij niet mogelijk.

        Args:
            (spelers) (dict): Alle spelers en hun gegevens
            speler (str): Naam van de speler die het commando uitvoert.
            args (str): Naam van het doelwit.
        """

        ## Bepaalt het doelwit
        doelwit = args[0] if not spelers[args[0]]['robbie_rotten'] else spelers[args[0]]['robbie_rotten']

        ## Zorgt ervoor dat de blocker en blockwolf niet geblokkeerd kunnen worden
        if spelers[doelwit]['rol'] in ['blocker', 'blockwolf']:
            plan_bericht(spelers[doelwit]['telefoonnummer'], 'Iemand probeerde je te blokkeren, maar dat is niet gelukt.', zendtijd(9, 0))
        else:
            ## Opent commandos.json
            with open('data/commandos.json', 'r') as file:
                commandos = json.load(file)

            ## Schrijft een nieuwe json zonder commandos van het doelwit
            commandos = [entry for entry in commandos if entry['speler'] != doelwit]

            ## Schrijft commandos terug naar bestand
            with open('data/commandos.json', 'w') as file:
                json.dump(commandos, file, indent = 4)
            
            ## Stuurt bericht naar doelwit
            plan_bericht(spelers[doelwit]['telefoonnummer'], 'Je bent geblokkeerd.', zendtijd(9, 0))
            spelers[speler]['doelwit'] = doelwit
    


class eigen_rechter(rol):
    rol =               'eigen_rechter'
    aura =              'onbekend'
    bondgenootschap =   'burgers'
    nachtimmuun =       False
    @with_spelers
    @staticmethod
    def afzetten(spelers, speler, kandidaat):
        """Zet een burgemeester af als dit mogelijk is en geeft feedback.

        Args:
            (spelers) (dict): Alle spelers en hun gegevens.
            speler (str): Naam van de speler die het commando uitvoert.
            kandidaat (str): Naam van de nieuwe burgemeester 

        Returns:
            str: Feedback die naar de speler wordt gestuurd.
        """

        ## Genereert algemene feedback
        feedback = basis_feedback(spelers, speler, ['afzetten'], 'altijd', kandidaat)
        if not feedback:

            ## Vertelt de speler dat er nog geen burgemeester is aangewezen
            if not any(speler['burgemeester'] == True for speler in spelers):
                return f'Er is nog geen burgemeester aangewezen.'
            
            ## Vertelt de speler dat deze kracht al is gebruikt
            if spelers[speler]['afzetten_ingezet']:
                return f'Je hebt al een burgemeester afgezet.'
            
            ## Bepaalt wie nu burgemeester is
            burgemeester = next((name for name, info in spelers.items() if info["burgemeester"]), None)

            ## Vertelt de speler dat deze persoon nu al burgemeester is
            if kandidaat == speler:
                return f'Deze speler is nu al burgemeester.'

            ## Zet de oude burgemeester af en stelt de nieuwe aan. Verbruikt ook de kracht
            spelers[burgemeester]['burgemeester'] = False
            spelers[kandidaat]['burgemeester'] = True
            spelers[speler]['afzetten_ingezet'] = True

            ## Stuurt het nieuws naar het dorp
            plan_bericht(naam_nummer('dorp_app'), f'{speler.capitalize()} heeft besloten om {burgemeester.capitalize()} af te zetten en {kandidaat.capitalize()} de nieuwe burgemeester te maken!')

            ## Geeft feedback
            return f'Check!'
        
        ## Geeft algemene feedback
        else:
            return feedback
    
    @with_spelers
    @staticmethod
    def stemming(spelers, speler, doelwit):
        """Beïnvloed de stemmen als dit mogelijk is zodat het doelwit altijd wint.

        Args:
            (spelers) (dict): Alle spelers en hun gegevens.
            speler (str): Naam van de speler die het commando uitvoert.
            doelwit (str): Naam van de persoon waarop gestemd moet worden.

        Returns:
            str: Feedback die naar de speler wordt gestuurd.
        """

        ## Genereert algemene feedback
        feedback = basis_feedback(spelers, speler, ['stemming'], 'stemmen', doelwit)
        if not feedback:

            ## Vertelt de speler dat de stemming niet beïnvloed kan worden op verkiezingsdag
            if not any(spelers[speler_]['burgemeester'] == True for speler_ in spelers):
                return f'Je kunt de stemming de eerste dag niet beïnvloeden.'
            
            ## Vertelt de speler dat deze kracht al is ingezet
            if spelers[speler]['stemming_ingezet']:
                return f'Je hebt al een stemming beïnvloed.'

            eigen_rechter = next((naam for naam in spelers if spelers[naam]["stemming_ingezet"] == 'dictatorwolf'), None)
            if eigen_rechter:
                return f'Er is al met de stemming geknoeid.'
            
            ## Zorgt ervoor dat het doelwit een overweldigend aantal stemmen krijgt en registreert dit voor het verhaal
            for speler in spelers:
                spelers[doelwit]['stemmen'] += len(spelers)
                spelers[speler]['stemming_ingezet'] = True
                spelers[speler]['stemming_beinvloed'] = 'eigen_rechter'

            ## Geeft feedback
            return f'Check!'
        
        ## Geeft algemene feedback
        else:
            return feedback
    


class hoer(rol):
    rol =               'hoer'
    aura =              'goed'
    bondgenootschap =   'burgers'
    nachtimmuun =       False
    @with_spelers
    @staticmethod
    def verblijven(spelers, speler, doelwit):
        """Registreert het verblijven van de speler bij het doelwit als dit mogelijk is en geeft feedback.

        Args:
            (spelers) (dict): Alle spelers en hun gegevens
            speler (str): Naam van de speler die het commando uitvoert.
            doelwit (str): Naam van het doelwit.

        Returns:
            str: Feedback die naar de speler wordt gestuurd
        """

        ## Genereert algemene feedback
        feedback = basis_feedback(spelers, speler, ['verblijven'], 'avond', doelwit)
        if not feedback:

            ## Vertelt de speler dat hij/zij niet twee keer achter elkaar bij dezelfde speler kan verblijven
            if spelers[speler]['doelwit'] == doelwit:
                return f'Je kunt niet twee keer achter elkaar bij dezelfde persoon verblijven.'
            
            ## Vertelt de speler dat hij/zij niet bij zichzelf kan verblijven
            if speler == doelwit:
                return f'Je kunt niet bij jezelf verblijven.'
            
            ## Zet het commando in de wacht
            verwerk_commando(spelers, speler, 'verblijven_verwerken', doelwit)

            ## Geeft feedback
            return f'Check!'
        
        ## Geeft algemene feedback
        else:
            return feedback
    
    @with_spelers
    @staticmethod
    def verblijven_verwerken(spelers, speler, *args):
        """Verwerkt het commando verblijven van de hoer. Verandert zijn/haar locatie.

        Args:
            (spelers) (str): Alle spelers en hun gegevens
            speler (str): Naam van de speler die het commando uitvoert.
        """

        ## Bepaalt het doelwit
        doelwit = args[0] if not spelers[args[0]]['robbie_rotten'] else spelers[args[0]]['robbie_rotten']

        ## Hoer gaat dood bij slapen bij de moloch na de 3e moord
        if int(spelers[doelwit]['moloch_kracht']) > 2:
            spelers = dood(spelers, doelwit, speler, f"moloch_{spelers[doelwit]['moloch_kracht']}")
    
        else:
            ## Verandert de locatie van de speler
            spelers[speler]['locatie'] = doelwit

            ## Bedrenkt het doelwit als de hoer ook bedrenkt is
            if spelers[speler]['bedrenkt']:
                spelers[doelwit]['bedrenkt'] = True        

            ## Stuurt de speler de straat op
            spelers[speler]['op_straat'] = True

            ## Geeft het doelwit een gast
            spelers[doelwit]['gasten'].append((speler, 'blijft slapen'))

            ## Registreert het laatste doelwit van de speler
            spelers[speler]['doelwit'] = doelwit
    


class jager(rol):
    rol =               'jager'
    aura =              'onbekend'
    bondgenootschap =   'burgers'
    nachtimmuun =       False
    
    @with_spelers
    @staticmethod
    def schieten(spelers, speler, doelwit):
        """Schiet iemand dood als dit mogelijk is en geeft feedback.

        Args:
            (spelers) (dict): Alle spelers en hun gegevens.
            speler (str): Naam van de speler die het commando uitvoert.
            doelwit (str): Naam van het doelwit

        Returns:
            str: Feedback die naar de speler wordt gestuurd
        """

        ## Opent de huidige geregistreerde commando's
        with open('data/commandos.json', 'r') as file:
            commandos = json.load(file)

        ## Vertelt de speler dat deze kracht al is ingezet
        if spelers[speler]['kracht_ingezet']:
            return f'Je hebt al een speler neergeschoten.'
        
        ## Vertelt de speler dat hij/zij nog niet dood is
        if not spelers[speler]['dood']:
            return f'Je bent nog niet dood.'
        
        ## Vertelt de speler dat het doelwit al dood is
        if doelwit and spelers.get(doelwit, {}).get('dood'):
            return f'Deze speler is al dood.'
        
        ## Doodt het doelwit
        spelers[doelwit]['dood'] = True

        ## Registreert het inzetten van deze kracht
        spelers[speler]['kracht_ingezet'] = True

        ## Stuurt het nieuws in de dorps app
        plan_bericht(naam_nummer('dorp_app'), f"De geest van {speler.capitalize()} richt de loop op {doelwit.capitalize()}, waarna {doelwit.capitalize()} ter plekke overlijdt.\n\n{doelwit.capitalize()} was {spelers[doelwit]['rol'].replace('_', ' ')}")

        ## Verwijderd de commando's van het doelwit
        commandos = [entry for entry in commandos if entry['speler'] != doelwit]

        ## Slaat de commando's weer op
        with open('data/commandos.json', 'w') as file:
            json.dump(commandos, file, indent = 4)



class stiekeme_kind(rol):
    rol =               'stiekeme_kind'
    aura =              'goed'
    bondgenootschap =   'burgers'
    nachtimmuun =       False

    @with_spelers
    @staticmethod
    def spieken(spelers, speler):
        """Laat het stiekeme kind spieken in de wolvenapp en geeft feedback.

        Args:
            (spelers) (dict): Alle spelers en hun gegevens
            speler (str): Naam van de speler die het commando uitvoert.

        Returns:
            str: Feedback of de gelezen berichten
        """

        ## Genereert algemene feedback
        feedback = basis_feedback(spelers, speler, ['spieken'], 'stiekeme_kind')
        if not feedback:

            ## Vertelt het stiekeme kind dat er vandaag al gespiekt is
            if spelers[speler]['gespiekt']:
                return f'Je hebt vandaag al gespiekt.'

            ## Plaatst het verzoek en verkrijgt de berichten
            response = requests.post("http://127.0.0.1:3000/fetch_messages",
                json={"group_id": naam_nummer('wolven_app'), "limit": 2})

            ## Lijst van alle berichten die later worden samengevoegd
            bericht = ['Je ziet de volgende berichten:']

            ## Als het verzoek succesvol is worden
            if response.status_code == 200:

                ## Berichten worden gelezen in een JSON format
                messages = response.json()

                ## De originele berichten worden gelezen
                for index, message in enumerate(messages):
                    message_body = message['body']

                    # Alle namen worden "zwartgelakt"
                    for naam in spelers.keys():
                        message_body = re.sub(rf'\b{naam}\b', '███', message_body, flags=re.IGNORECASE)

                    # Alle mentions of tags worden "Zwartgelakt"
                    mention_pattern = r'@(\d{5,15})(?:@c\.us)?'
                    message_body = f'Bericht {index + 1}' + '\n' + re.sub(mention_pattern, '███', message_body) 

                    ## Berichten worden verzameld in een lijst
                    bericht.append(message_body)

            ## Het bericht wordt samengevoegd
            bericht = '\n\n'.join(bericht)

            ## De kracht wordt voor deze dag als ingezet geregistreerd
            spelers[speler]['gespiekt'] = True

            ## Geeft de berichten of feedback
            return bericht
        
        ## Geeft algemene feedback
        else:
            return feedback



class waarzegger(rol):
    rol =               'waarzegger'
    aura =              'goed'
    bondgenootschap =   'burgers'
    nachtimmuun =       False

    @with_spelers
    @staticmethod
    def lezen(spelers, speler, doelwit):
        """Registreert het commando lezen van de waarzegger als dit mogelijk is en geeft feedback.

        Args:
            (spelers) (dict): Alle spelers en hun gegevens
            speler (str): Naam van de speler die het commando uitvoert.
            doelwit (str): Naam van het doelwit.

        Returns:
            str: Feedback die naar de speler wordt gestuurd
        """

        ## Genereert algemene feedback
        feedback = basis_feedback(spelers, speler, ['lezen'], 'avond', doelwit)
        if not feedback:

            ## Vertelt de speler dat hij/zij niet twee keer dezelfde persoon mag lezen
            if spelers[speler]['doelwit'] == doelwit:
                return f'Je kunt niet twee keer achter elkaar dezelfde persoon lezen.'
            
            ## Registreert het commando
            verwerk_commando(spelers, speler, 'lezen_verwerken', doelwit)

            ## Geeft feedback
            return f'Check!'
        
        ## Geeft algemene feedback
        else:
            return feedback
    
    @with_spelers
    @staticmethod
    def lezen_verwerken(spelers, speler, *args):
        """Verwerkt het commando lezen van de waarzegger. Verstuurt de aura.

        Args:
            (spelers) (dict): Alle spelers en hun gegevens
            speler (str): Naam van de speler die het commando uitvoert.
        """

        ## Bepaalt het doelwit
        doelwit = args[0] if not spelers[args[0]]['robbie_rotten'] else spelers[args[0]]['robbie_rotten']

        ## Vertelt dat het doelwit niet thuis was
        if spelers[doelwit]['locatie'] != doelwit:
            plan_bericht(spelers[speler]['telefoonnummer'], f'Je doelwit was niet thuis!', zendtijd(9, 0))
            return

        ## Bepaalt of de speler slaaf is
        if spelers[doelwit]['rol'] == 'slaaf':
            plan_bericht(spelers[speler]['telefoonnummer'], f'Je doelwit heeft geen intenties naast het dienen van zijn/haar meester.', zendtijd(9, 0))
            return
        
        ## Bepaalt de aura die gelezen wordt
        gelezen_aura = spelers[doelwit]['tijdelijke_aura'] if spelers[doelwit]['tijdelijke_aura'] else spelers[doelwit]['aura']

        ## Geeft de gelezen aura
        plan_bericht(spelers[speler]['telefoonnummer'], f'De aura die je leest is {gelezen_aura}!', zendtijd(9, 0))

        ## Verandert het laatste doelwit van de speler
        spelers[speler]['doelwit'] = doelwit



class priester(rol):
    rol =               'priester'
    aura =              'goed'
    bondgenootschap =   'burgers'
    nachtimmuun =       False

    @with_spelers
    @staticmethod
    def gooien(spelers, speler, doelwit):
        """Gooit een flesje wijwater over het doelwit als dit mogelijk is en geeft feedback

        Args:
            (spelers) (dict): Alle spelers en hun gegevens
            speler (str): Naam van de speler die het commando uitvoert.
            doelwit (str): Naam van het doelwit

        Returns:
            str: Feedback die naar de speler wordt gestuurd
        """

        ## Genereert algemene feedback
        feedback = basis_feedback(spelers, speler, ['gooien'], 'priester', doelwit)
        if not feedback:

            ## Vertelt de speler dat deze kracht al is ingezet
            if spelers[speler]['kracht_ingezet']:
                return f'Je hebt je flesje wijwater al gegooid.'
            
            ## Als het doelwit gevoelig is voor wijwater
            if spelers[doelwit]['rol'] in ['zwarte_rat', 'heks', 'witte_wolf'] or spelers[doelwit]['bondgenootschap'] == 'wolven':

                ## Doodt het doelwit
                spelers[doelwit]['dood'] = True

                ## Registreert het inzetten van de kracht
                spelers[speler]['kracht_ingezet'] = True

                ## Stuurt het nieuws naar de dorps app
                plan_bericht(naam_nummer('dorp_app'), f"De heilig verklaarde {speler.capitalize()} Gooit een flesje wijwater richting {doelwit.capitalize()}, waarna {doelwit.capitalize()} ter plekke zwicht voor de kracht van het geloof.\n\n{doelwit.capitalize()} was {spelers[doelwit]['rol'].replace('_', ' ')}")

                ## Geeft feedback
                return 'Check!'
            
            ## Als het doelwit niet gevoelig is voor het wijwater
            else:

                ## Registreert het inzetten van de kracht
                spelers[speler]['kracht_ingezet'] = True

                ## Stuurt het nieuws naar de dorps app
                plan_bericht(naam_nummer('dorp_app'), f"De heilig verklaarde {speler.capitalize()} Gooit een flesje wijwater richting {doelwit.capitalize()}. {doelwit.capitalize()} schudt zich af, haalt de schouders op en loopt door.")

                ## Geeft feedback
                return 'Check!'
        
        ## Geeft algemene feedback
        else:
            return feedback



class dr_frankenstein(rol):
    rol =               'dr_frankenstein'
    aura =              'onbekend'
    bondgenootschap =   'burgers'
    nachtimmuun =       False

    @with_spelers
    @staticmethod
    def maken(spelers, speler, doelwit, reserve):
        """Registreert het commando maken van Dr. Frankenstein als dit mogelijk is en geeft feedback.

        Args:
            (spelers) (dict): Alle spelers en hun gegevens
            speler (str): Naam van de speler die het commando uitvoert.
            doelwit_rol (str): Naam van het doelwit dat terug tot leven wordt gewekt.
            reserve_rol (str): Naam van de reserve speler die wordt gebruikt als reserve onderdelen.

        Returns:
            str: Feedback die naar de speler wordt gestuurd.
        """

        dagdelen, tijd = dagdeel('dr_frankenstein')
        with open('data/commandos.json') as file:
            commandos = json.load(file)

        if 'dr_frankenstein' not in dagdelen:
            return f'Je kunt deze actie alleen uitvoeren tussen {" en ".join(tijd)}.'
        if any(entry["speler"] == speler and entry["commando"] in [f'{c}_verwerken' for c in ['dr_frankenstein']] for entry in commandos):
            return f'Je mag dit commando niet meer uitvoeren. Gebruik /reset <actie> om dit ongedaan te maken.'
        if spelers[speler]['dood']:
            return f'Je bent al dood.'


        ## Vertelt de speler dat zichzelf gebruiken niet mogelijk is
        if speler in [doelwit, reserve]:
            return f'Je kunt jezelf niet gebruiken om een lichaam te bouwen.'

        ## Vertelt de speler dat een speler nog leeft
        if not spelers[doelwit]['dood']:
            return f'{doelwit.capitalize()} is nog niet dood.'
        if not spelers[reserve]['dood']:
            return f'{reserve.capitalize()} is nog niet dood.'
        
        ## Vertelt de speler dat een speler al te lang dood is
        if not spelers[doelwit]['huidig_dood']:
            return f'{doelwit.capitalize()} is al te lang dood.'
        if not spelers[reserve]['huidig_dood']:
            return f'{reserve.capitalize()} is al te lang dood.'

        ## Vertelt de speler dat een persoon niet meer gebruikt kan worden
        if spelers[doelwit]['levensduur'] < 0:
            return f'{doelwit.capitalize()} kan niet meer terug tot leven worden gewekt.'
        if spelers[reserve]['levensduur'] < 0:
            return f'{reserve.capitalize()} kan niet meer worden gebruikt voor onderdelen.'
        
        ## Vertelt de speler dat een rol niet als doelwit kan worden gebruikt
        if spelers[doelwit]['bondgenootschap'] != 'burgers':
            return f'Deze persoon kan niet terug tot leven worden gewekt.'
        
        spelers = dr_frankenstein.maken_verwerken(spelers, speler, doelwit, reserve)
        return f'Check!'
            
    

    def maken_verwerken(spelers, speler, *args):
        ## Bepaalt het doelwit
        doelwit = args[0]
        reserve = args[1]

        ## Wekt de het doelwit weer tot leven
        spelers[doelwit]['dood'] = False
        spelers[doelwit]['huidig_dood'] = False
        spelers[doelwit]['levensduur'] = 2
        spelers[doelwit]['monster'] = True
        spelers[doelwit]['tot_leven_gewekt'] = True

        ## Verwerkt de reserve persoon
        spelers[reserve]['levensduur'] = -1

        return spelers



class gewonde(rol):
    rol =               'gewonde'
    aura =              'onbekend'
    bondgenootschap =   'burgers'
    nachtimmuun =       False



class robbie_rotten(rol):
    rol =               'robbie_rotten'
    aura =              'onbekend'
    bondgenootschap =   'burgers'
    nachtimmuun =       False

    @with_spelers
    @staticmethod
    def vermommen(spelers, speler, doelwit):
        """Registreert het vermommen van robbie rotten als dat mogelijk is en geeft feedback

        Args:
            (spelers) (dict): Alle spelers en hun gegevens
            speler (str): Naam van de speler die het commando uitvoert.
            doelwit (str): Naam van het doelwit

        Returns:
            _type_: _description_
        """

        ## Genereert basis feedback
        feedback = basis_feedback(spelers, speler, ['vermommen'], 'avond', doelwit)
        if not feedback:

            
            if spelers[speler]['doelwit'] == doelwit:
                return f'Je kunt jezelf niet twee keer achter elkaar als dezelfde persoon vermommen.'
            verwerk_commando(spelers, speler, 'vermommen_verwerken', doelwit)
            return 'Check!'
        else:
            return feedback
        
    @with_spelers
    @staticmethod
    def vermommen_verwerken(spelers, speler, *args):
        doelwit = args[0] if not spelers[args[0]]['robbie_rotten'] else spelers[args[0]]['robbie_rotten']
        spelers[speler]['robbie_rotten'] = doelwit
        spelers[doelwit]['robbie_rotten'] = speler
        test(f'doelwit: {doelwit}, speler: {speler}')



class spion(rol):
    rol =               'spion'
    aura =              'goed'
    bondgenootschap =   'burgers'
    nachtimmuun =       False

    @with_spelers
    @staticmethod
    def spioneer(spelers, speler, huis):
        feedback = basis_feedback(spelers, speler, ['spioneer'], 'avond', huis)
        if not feedback:
            verwerk_commando(spelers, speler, 'spioneer_verwerken', huis)
            return f'Check!'
        else:
            return feedback
        
    @with_spelers
    @staticmethod
    def spioneer_verwerken(spelers, speler, *args):
        huis = args[0]
        bericht = ['De volgende personen bezoeken het huis van je doelwit:']

        ## Verandert de locatie van de speler
        spelers[speler]['locatie'] = huis
        spelers[speler]['op_straat'] = True

        for bezoeker in spelers[huis]['gasten']:
            if spelers[bezoeker]['rol'] != 'glitch':
                persoon = bezoeker[0] if not spelers[bezoeker[0]]['robbie_rotten'] else spelers[bezoeker[0]]['robbie_rotten']
                bericht.append(f'{persoon} {bezoeker[1]}')
        plan_bericht(spelers[speler]['telefoonnummer'], '\n'.join(bericht), zendtijd(9, 0))



class transporteur(rol):
    rol =               'transporteur'
    aura =              'goed'
    bondgenootschap =   'burgers'
    nachtimmuun =       False

    @with_spelers
    @staticmethod
    def transporteer(spelers, speler, doelwit_1, doelwit_2):
        feedback = basis_feedback(spelers, speler, ['transporteer'], 'avond', doelwit_1, doelwit_2)
        if not feedback:
            verwerk_commando(spelers, speler, 'transporteer_verwerken', doelwit_1, doelwit_2)
            return f'Check!'
        else:
            return feedback
    
    @with_spelers
    @staticmethod
    def transporteer_verwerken(spelers, speler, args):
        doelwit_1 = args[0] if not spelers[args[0]]['robbie_rotten'] else spelers[args[0]]['robbie_rotten']
        doelwit_2 = args[1] if not spelers[args[1]]['robbie_rotten'] else spelers[args[1]]['robbie_rotten']

        spelers[doelwit_1]['robbie_rotten'] = doelwit_2
        spelers[doelwit_2]['robbie_rotten'] = doelwit_1



class vigilant(rol):
    rol =               'vigilant'
    aura =              'onbekend'
    bondgenootschap =   'burgers'
    nachtimmuun =       False

    @with_spelers
    @staticmethod
    def schieten(spelers, speler, doelwit):
        feedback = basis_feedback(spelers, speler, ['schieten'], 'avond', doelwit)
        if not feedback:
            if spelers[speler]['kogels'] < 1:
                return f'Je hebt al je kogels al verbruikt.'
            verwerk_commando(spelers, speler, 'schieten_verwerken', doelwit)
            return f'Check!'
        else:
            return feedback
    
    @with_spelers
    @staticmethod
    def schieten_verwerken(spelers, speler, *args):
        doelwit = args[0] if not spelers[args[0]]['robbie_rotten'] else spelers[args[0]]['robbie_rotten']

        ## Stuurt de vigilant de straat op
        spelers[speler]['locatie'] = doelwit
        spelers[speler]['op_straat'] = True

        if spelers[doelwit]['nachtimmuun']:
            plan_bericht(spelers[speler]['telefoonnummer'], 'Je doelwit was te sterk.', zendtijd(9, 0))
            spelers[speler]['kogels'] -= 1
        else:
            spelers = dood(spelers, speler, doelwit, 'schieten')
            spelers[speler]['kogels'] -= 1



class lijfwacht(rol):
    rol =               'lijfwacht'
    aura =              'goed'
    bondgenootschap =   'burgers'
    nachtimmuun =       False

    @with_spelers
    @staticmethod
    def bescherm(spelers, speler, doelwit):
        feedback = basis_feedback(spelers, speler, ['bescherm'], 'avond', doelwit)
        if not feedback:
            if speler == doelwit and spelers[speler]['lijfwacht'] < 2:
                return f'Je kunt jezelf niet meer beschermen.'
            verwerk_commando(spelers, speler, 'bescherm_verwerken', doelwit)
            return f'Check!'
        else:
            return feedback
    
    @with_spelers
    @staticmethod
    def bescherm_verwerken(spelers, speler, *args):
        doelwit = args[0] if not spelers[args[0]]['robbie_rotten'] else spelers[args[0]]['robbie_rotten']
        spelers[speler]['locatie'] = doelwit
        spelers[speler]['op_straat'] = True
        spelers[doelwit]['lijfwacht_bescherming'] = speler



class vogelspotter(rol):
    rol =               'vogelspotter'
    aura =              'goed'
    bondgenootschap =   'burgers'
    nachtimmuun =       False

    @with_spelers
    @staticmethod
    def spotten(spelers, speler, kans):
        feedback = basis_feedback(spelers, speler, ['spotten'], 'avond')
        if not feedback:
            if not kans.isnumeric():
                return f'Deze input wordt niet geaccepteerd.'
            else:
                kans = int(kans)
            if spelers[speler]['cooldown'] >= 1:
                return f'Je kunt niet op pad om vogels te spotten.'
            if kans > spelers[speler]['kans']:
                return f"Dit getal wordt niet geaccepteerd. Geef een getal tussen de 1 en {spelers[speler]['kans']}."
            verwerk_commando(spelers, speler, 'spotten_verwerken', kans)
            return f'Check!'
        else:
            return feedback
    
    @with_spelers
    @staticmethod
    def spotten_verwerken(spelers, speler, *args):
        kans = args[0]
        getal = random.randint(1, spelers[speler]['kans'])
        spelers[speler]['locatie'] = 'straat'
        spelers[speler]['op_straat'] = True
        if kans == getal:
            op_straat = [speler_ for speler_ in spelers if spelers[speler_]['op_straat']]

            wolven = [speler_ for speler_ in op_straat if (spelers[speler_]['bondgenootschap'] == 'wolven' or spelers[speler_]['rol'] == 'witte_wolf')]

            wolf = random.choice(wolven)
            wolf_naam = wolf if not spelers[wolf]['robbie_rotten'] else spelers[wolf]['robbie_rotten']
            plan_bericht(spelers[speler]['telefoonnummer'], f"Als je wakker wordt, zie je {wolf_naam.capitalize()} het huis van {spelers[wolf]['locatie'].capitalize()} verlaten!")

            spelers[speler]['kans'] += 1
            spelers[speler]['cooldown'] = 2

        
        else:
            return f'Je gok was fout!'



class dokter(rol):
    rol =               'dokter'
    aura =              'goed'
    bondgenootschap =   'burgers'
    nachtimmuun =       False

    @with_spelers
    @staticmethod
    def bescherm(spelers, speler, doelwit):
        feedback = basis_feedback(spelers, speler, ['bescherm'], 'avond', doelwit)
        if not feedback:
            if spelers[speler]['spuiten'] <= 0:
                return f'Je hebt geen spuiten meer om te zetten.'
            if speler == doelwit and spelers[speler]['lijfwacht'] < 2:
                return f'Je kunt jezelf niet meer beschermen.'
            verwerk_commando(spelers, speler, 'bescherm_verwerken', doelwit)
            return f'Check!'
        else:
            return feedback
    
    @with_spelers
    @staticmethod
    def bescherm_verwerken(spelers, speler, *args):
        doelwit = args[0] if not spelers[args[0]]['robbie_rotten'] else spelers[args[0]]['robbie_rotten']
        if speler == doelwit:
            spelers[speler]['zelf_beschermd'] = True
            spelers[speler]['dokter_bescherming'] = speler
            spelers[speler]['spuiten'] += -1
        else:
            spelers[speler]['op_straat'] = True
            spelers[speler]['locatie'] = doelwit
            spelers[doelwit]['dokter_bescherming'] = speler
    


class cipier(rol):
    rol =               'cipier'
    aura =              'goed'
    bondgenootschap =   'burgers'
    nachtimmuun =       False

    @with_spelers
    @staticmethod
    def vragen(spelers, speler, doelwit, vraag):
        dagdelen, tijd = dagdeel('avond')
        if spelers[speler]['dood']:
            return f'Je bent al dood.'
        if 'avond' not in dagdelen:
            return f'Je kunt deze actie alleen uitvoeren tussen {" en ".join(tijd)}.'
        if speler == doelwit:
            return f'Je kunt jezelf niet opsluiten.'
        if doelwit != None and doelwit not in spelers:
            return f'Deze speler speelt niet mee of is verkeerd gespeld.'
        if doelwit and spelers.get(doelwit, {}).get('dood'):
            return f'Deze speler is al dood.'
        if spelers[speler]['doelwit'] == doelwit:
            return f'Je mag niet twee keer achter elkaar dezelfde speler opsluiten.'

        with open('data/commandos.json', 'r') as file:
            commandos = json.load(file)

        gestelde_vragen = sum(1 for entry in commandos if entry["speler"] == speler and entry["commando"] == 'vragen_verwerken')
        if gestelde_vragen >= 3:
            return f'Je hebt al je vragen al gesteld.'
        
        intro = True if gestelde_vragen == 0 else False

        target = next((entry["argumenten"][0] for entry in commandos
            if entry["speler"] == speler and entry["commando"] == 'vragen_verwerken'), None)
        
        if target != doelwit and target != None:
            return f'Je kunt de vraag alleen stellen aan de persoon die je op wilt sluiten.'
        
        verwerk_commando(spelers, speler, 'vragen_verwerken', doelwit, vraag, intro)
        return f'Check!'
    

    @with_spelers
    @staticmethod
    def vragen_verwerken(spelers, speler, *args):
        doelwit = args[0]
        vraag = args[1]
        intro = args[2]

        with open('data/commandos.json', 'r') as file:
            commandos = json.load(file)


        doelwit = args[0] if not spelers[args[0]]['robbie_rotten'] else spelers[args[0]]['robbie_rotten']
        vraag = args[1]

        spelers[doelwit]['locatie'] = f'{speler}_cipier'
        ## Opent commandos.json
        with open('data/commandos.json', 'r') as file:
            commandos = json.load(file)

        ## Schrijft een nieuwe json zonder commandos van het doelwit
        commandos = [entry for entry in commandos if entry['speler'] != doelwit]

        ## Schrijft commandos terug naar bestand
        with open('data/commandos.json', 'w') as file:
            json.dump(commandos, file, indent = 4)
        
        ## Stuurt een intro:
        if intro:
            plan_bericht(spelers[doelwit]['telefoonnummer'], 'Je bent gevangen genomen! Geef antwoord op deze vragen door /antwoorden <antwoord> te gebruiken. Let op! Slecht\'s één antwoord per commando.')
            spelers[speler]['vragen'].append(('intro'))

        ## Stelt de vraag
        plan_bericht(spelers[doelwit]['telefoonnummer'], vraag, zendtijd(22, 0))



class helderziende(rol):
    rol =               'helderziende'
    aura =              'goed'
    bondgenootschap =   'burgers'
    nachtimmuun =       False

    @with_spelers
    @staticmethod
    def zien(spelers, speler):
        feedback = basis_feedback(spelers, speler, ['zien'], 'avond')
        if not feedback:
            verwerk_commando(spelers, speler, 'zien_verwerken')
            return f'Check!'
        else:
            return feedback
    
    @with_spelers
    @staticmethod
    def zien_verwerken(spelers, speler, *args):
        schuldigen = [s for s in spelers if spelers[s]['bondgenootschap'] != 'burgers' and not spelers[s]['dood']]
        onschuldigen = [s for s in spelers if spelers[s]['bondgenootschap'] == 'burgers' and not spelers[s]['dood']]

        dag_type = 'even' if spelers[speler]['dag']%2 == 0 else 'oneven'
        resultaat = []

        if dag_type == 'oneven':
            totaal = 3
            # Minimaal 1 schuldig
            schuldig_aantal = 1 if schuldigen else 0
            schuldig_aantal = min(len(schuldigen), max(schuldig_aantal, totaal))
            onschuldig_aantal = min(len(onschuldigen), totaal - schuldig_aantal)

            resultaat.extend(random.sample(schuldigen, schuldig_aantal))
            resultaat.extend(random.sample(onschuldigen, onschuldig_aantal))

        elif dag_type == 'even':
            totaal = 2
            # Minimaal 1 onschuldig
            onschuldig_aantal = 1 if onschuldigen else 0
            onschuldig_aantal = min(len(onschuldigen), max(onschuldig_aantal, totaal))
            schuldig_aantal = min(len(schuldigen), totaal - onschuldig_aantal)

            resultaat.extend(random.sample(onschuldigen, onschuldig_aantal))
            resultaat.extend(random.sample(schuldigen, schuldig_aantal))

        # Shuffle to mix guilty/innocent
        random.shuffle(resultaat)

        if not resultaat:
            bericht = 'Er zijn momenteel geen spelers om te zien.'
        else:
            bericht = 'Je ziet de volgende namen:\n' + '\n'.join(resultaat)

        plan_bericht(spelers[speler]['telefoonnummer'], bericht, zendtijd(9, 0))



class quizmaster(rol):
    rol =               'quizmaster'
    aura =              'goed'
    bondgenootschap =   'burgers'
    nachtimmuun =       False

    @with_spelers
    @staticmethod
    def vragen(spelers, speler, doelwit, vraag):
        vraag = doelwit + vraag
        feedback = basis_feedback(spelers, speler, ['vragen'], 'ochtend')
        if not feedback:
            if spelers[speler]['cooldown'] > 0:
                return f'Je kunt nog geen vraag stellen.'
            with open('data/prompts/quizmaster.txt', 'r') as file:
                prompt = file.read()
                prompt = prompt.replace('<DATA>', str(spelers))
                prompt = prompt.replace('<VRAAG>', vraag)
                antwoord = genereer_bericht(prompt)

            if 'niet toegestaan' in antwoord.lower():
                return f'Deze vraag is niet toegestaan.\n\nDenk je dat dit een fout is? Gebruik /help voor hulp.'
            else:
                spelers[speler]['cooldown'] = 2
                return antwoord

        else:
            return feedback



class student(rol):
    rol =               'student'
    aura =              'onbekend'
    bondgenootschap =   'burgers'
    nachtimmuun =       False

    @with_spelers
    @staticmethod
    def feesten(spelers, speler):
        feedback = basis_feedback(spelers, speler, ['vragen'], 'avond')
        if not feedback:
            nu = datetime.now()
            if nu.weekday not in [4, 5, 6]:
                return f'Het is nog geen tijd om te feesten.'
            verwerk_commando(spelers, speler, 'feesten_verwerken')
            return f'Check!'
        else:
            return feedback
    
    @with_spelers
    @staticmethod
    def feesten_verwerken(spelers, speler, *args):
        keuze = random.choices(['zien', 'slapen'], weights = [0.75, 0.25], k=1)[0]
        if keuze == 'zien':
            wolven = [speler_ for speler_ in spelers if ((spelers[speler_]['bondgenootschap'] == 'wolven' or spelers[speler_]['rol'] == 'witte_wolf')) and spelers[speler_]['op_straat']]
            spelers[speler]['op_straat'] = True
            spelers[speler]['locatie'] = 'straat'
            if not wolven:
                keuze = 'slapen'
            else:
                spelers[speler]['op_straat'] = False
                spelers[speler]['locatie'] = 'slapen'
                plan_bericht(spelers[speler]['telefoonnummer'], f'Na een mooie avond uit zie je {random.choice(wolven).capitalize()} over straat dwalen.')
        if keuze == 'slapen':
            ''



class agent(rol):
    rol =               'agent'
    aura =              'slecht'
    bondgenootschap =   'burgers'
    nachtimmuun =       False

    @with_spelers
    @staticmethod
    def patrouille(spelers, speler):
        feedback = basis_feedback(spelers, speler, ['patrouille'], 'avond')
        if not feedback:
            verwerk_commando(spelers, speler, 'patrouille_verwerken')
            return f'Check!'
        else:
            return feedback
        
    @with_spelers
    @staticmethod
    def patrouille_verwerken(spelers, speler, *args):
        wolven = [s for s in spelers if ((spelers[s]['bondgenootschap'] == 'wolven' or spelers[s]['rol'] == 'witte_wolf')) and spelers[s]['op_straat']]
        neutralen = [s for s in spelers if spelers[s]['bondgenootschap'] == 'neutralen' and spelers[s]['op_straat']]
        burgers = [s for s in spelers if spelers[s]['bondgenootschap'] == 'burgers' and spelers[s]['op_straat']]

        groepen = [wolven, neutralen, burgers]
        gewichten = [0.6, 0.2, 0.2]

        geldige_groepen = [(g, w) for g, w in zip(groepen, gewichten) if g]
        if not geldige_groepen:
            doelwit = None

        groepen, gewichten = zip(*geldige_groepen)
        op_straat = [random.choice(g) for g in groepen]
        doelwit = random.choices(op_straat, weights=gewichten, k=1)[0]

        if not doelwit:
            plan_bericht(spelers[speler]['telefoonnummer'], 'Het was rustig op straat.')
        else:
            spelers[doelwit]['locatie'] = 'agent'
            spelers[doelwit]['gearresteerd'] = True

            with open('data/commandos.json', 'r') as file:
                commandos = json.load(file)

            ## Schrijft een nieuwe json zonder commandos van het doelwit
            commandos = [entry for entry in commandos if entry['speler'] != doelwit]

            ## Schrijft commandos terug naar bestand
            with open('data/commandos.json', 'w') as file:
                json.dump(commandos, file, indent = 4)

            plan_bericht(spelers[doelwit]['telefoonnummer'], 'Je bent gearresteerd!', zendtijd(9, 0))
            plan_bericht(spelers[speler]['telefoonnummer'], f'Je hebt {doelwit.capitalize()} gearresteerd!', zendtijd(9, 0))



class gokker(rol):
    rol =               'gokker'
    aura =              'goed'
    bondgenootschap =   'burgers'
    nachtimmuun =       False

    @with_spelers
    @staticmethod
    def gok(spelers, speler, doelwit, inzet):
        if not inzet.isnumeric():
            return f'Dit is geen geldige inzet.'
        feedback = basis_feedback(spelers, speler, ['gok'], 'avond', doelwit)
        if not feedback:
            if int(spelers[speler]['balans']) < int(inzet):
                return f'Je balans is niet hoog genoeg om dit bedrag in te zetten.'
            verwerk_commando(spelers, speler, 'gok_verwerken', doelwit, inzet)
            return f'Check!'
        else:
            return feedback
    
    @with_spelers
    @staticmethod
    def gok_verwerken(spelers, speler, *args):
        doelwit = args[0]
        inzet = int(args[1])

        doden = [speler_ for speler_ in spelers if spelers[speler_]['huidig_dood'] and not spelers[speler_]['dood']]
        levenden = [speler_ for speler_ in spelers if not spelers[speler_]['huidig_dood'] and not spelers[speler_]['dood']]
        
        if len(doden) == 0:
            plan_bericht(spelers[speler]['telefoonnummer'], f"Je huidige balans is {spelers[speler]['balans']} WDD.", zendtijd(9, 0))

        elif spelers[speler]['dag'] == 'even':
            spelers[speler]['balans'] = int(spelers[speler]['balans']) - inzet
            if doelwit in doden:
                inzet = round(inzet * 2)
                spelers[speler]['balans'] = int(spelers[speler]['balans']) + inzet
                plan_bericht(spelers[speler]['telefoonnummer'], f"Je gok was goed! Je huidige balans is nu {spelers[speler]['balans']} WDD.", zendtijd(9, 0))
            else:
                plan_bericht(spelers[speler]['telefoonnummer'], f"Je gok was fout. Je huidige balans is nu {spelers[speler]['balans']} WDD.", zendtijd(9, 0))
        
        elif spelers[speler]['dag'] == 'oneven':
            spelers[speler]['balans'] = int(spelers[speler]['balans']) - inzet
            if doelwit in levenden:
                inzet = round(inzet * 1.5)
                spelers[speler]['balans'] = int(spelers[speler]['balans']) + inzet
                plan_bericht(spelers[speler]['telefoonnummer'], f"Je gok was goed! Je huidige balans is nu {spelers[speler]['balans']} WDD.", zendtijd(9, 0))
            else:
                plan_bericht(spelers[speler]['telefoonnummer'], f"Je gok was fout. Je huidige balans is nu {spelers[speler]['balans']} WDD.", zendtijd(9, 0))

    
    @with_spelers
    @staticmethod
    def balans(spelers, speler):
        return f"Je huidige balans is {spelers[speler]['balans']} WDD."






class cupido(rol):
    rol =               'cupido'
    aura =              'onbekend'
    bondgenootschap =   'neutralen'
    nachtimmuun =       1

    @with_spelers
    @staticmethod
    def koppel(spelers, speler, doelwit_1, doelwit_2):
        feedback = basis_feedback(spelers, speler, ['koppel'], 'avond', doelwit_1, doelwit_2)
        if not feedback:
            tortelduifjes = [speler_ for speler_ in spelers if spelers[speler_]['tortelduifje']]
            if spelers[speler]['koppel_gemaakt'] == 'klaar':
                return f'Je kunt geen koppels meer maken.'
            if len(tortelduifjes) > 0:
                return f'Er zijn nog twee tortelduifjes in leven.'
            verwerk_commando(spelers, speler, 'koppel_verwerken', doelwit_1, doelwit_2)
            return f'Check!'
        else:
            return feedback
    
    @with_spelers
    @staticmethod
    def koppel_verwerken(spelers, speler, *args):
        doelwit_1 = args[0]
        doelwit_2 = args[1]

        if spelers[speler]['koppel_gemaakt'] == 'gemist':
            spelers[speler]['koppel_gemaakt'] = 'klaar'
        
        for doelwit in [doelwit_1, doelwit_2]:
            spelers[doelwit]['tortelduifje'] = True
        
        plan_bericht(spelers[doelwit_1]['telefoonnummer'], f'Jij hebt vanaf nu een liefdesrelatie met {doelwit_2.capitalize()}', zendtijd(9, 0))
        plan_bericht(spelers[doelwit_2]['telefoonnummer'], f'Jij hebt vanaf nu een liefdesrelatie met {doelwit_1.capitalize()}', zendtijd(9, 0))



class heks(rol):
    rol =               'heks'
    aura =              'onbekend'
    bondgenootschap =   'neutralen'
    nachtimmuun =       1

    @with_spelers
    @staticmethod
    def dodenlijst(spelers, speler):
        feedback = basis_feedback(spelers, speler, ['drankje'], 'nacht')
        if not feedback:
            doden = [speler_ for speler_ in spelers if spelers[speler_]['huidig_dood'] and not spelers[speler_]['dood']]
            return ('De volgende mensen overlijden vannacht:\n- ' + '\n- '.join(doden))
        else:
            return feedback
    
    @with_spelers
    @staticmethod
    def drankjes(spelers, speler):
        drankjes_dict = {'doden': 'Drankje om te doden', 'helen': 'Drankje om te helen', 'rol': 'Drankje om iemands rol te achterhalen'}
        return 'Je hebt de volgende drankjes:\n- ' + '\n- '.join([f'{drank}: {drankjes_dict[drank]}' for drank in spelers[speler]['drankjes']])
    
    @with_spelers
    @staticmethod
    def drankje(spelers, speler, doelwit, drank):
        feedback = basis_feedback(spelers, speler, ['drankje'], 'nacht')
        if not feedback:
            if drank not in ['doden', 'helen', 'rol']:
                return f'Dit is geen valide drankje.'
            if drank not in spelers[speler]['drankjes']:
                return f'Je hebt dit drankje al gebruikt.'
            if drank == 'doden':
                if spelers[doelwit]['huidig_dood']:
                    return f'Deze speler gaat vannacht al dood.'
            if drank == 'helen':
                if not spelers[doelwit]['huidig_dood']:
                    return f'Deze speler gaat vannacht niet dood.'
            verwerk_commando(spelers, speler, 'drankje_verwerken', doelwit, drank)
            return f'Check!'
        else:
            return feedback
    
    @with_spelers
    @staticmethod
    def drankje_verwerken(spelers, speler, *args):
        doelwit = args[0]
        drank = args[1]
        
        spelers[speler]['drankjes'].remove(drank)

        if drank == 'doden':
            spelers = dood(spelers, speler, doelwit, 'magie')

        if drank == 'helen':
            if spelers[doelwit]['spiegelwolf']:
                pass
            else:
                spelers[doelwit]['dood'] = False
                spelers[doelwit]['huidig_dood'] = False
        
        if drank == 'rol':
            plan_bericht(spelers[speler]['telefoonnummer'], f"{doelwit.capitalize()} heeft de volgende rol: {spelers[doelwit]['rol'].replace('_', ' ')}.", zendtijd(9, 0))



class blinde_gek(rol):
    rol =               'blinde_gek'
    aura =              'onbekend'
    bondgenootschap =   'neutralen'
    nachtimmuun =       1



class pyromaan(rol):
    rol =               'pyromaan'
    aura =              'onbekend'
    bondgenootschap =   'neutralen'
    nachtimmuun =       1

    @with_spelers
    @staticmethod
    def bedrenken(spelers, speler, doelwit):
        feedback = basis_feedback(spelers, speler, ['bedrenken', 'schoonmaken', 'aansteken'], 'avond', doelwit)
        if not feedback:
            if doelwit == speler:
                return f'Je kunt jezelf niet bedrenken.'
            verwerk_commando(spelers, speler, 'bedrenken_verwerken', doelwit)
            return f'Check!'
        else:
            return feedback
    
    @with_spelers
    @staticmethod
    def bedrenken_verwerken(spelers, speler, *args):
        doelwit = args[0] if not spelers[args[0]]['robbie_rotten'] else spelers[args[0]]['robbie_rotten']
        spelers[doelwit]['bedrenkt'] = True
        bedrenkten = [speler_ for speler_ in spelers if spelers[speler_]['bedrenkt']]
        plan_bericht(spelers[speler]['telefoonnummer'], 'De volgende personen zijn bedrenkt:\n- ' + '\n- '.join(bedrenkten), zendtijd(9, 0))
    
    @with_spelers
    @staticmethod
    def schoonmaken(spelers, speler):
        feedback = basis_feedback(spelers, speler, ['bedrenken', 'schoonmaken', 'aansteken'], 'avond')
        if not feedback:
            if not spelers[speler]['bedrenkt']:
                return f'Je bent niet bedrenkt.'
            verwerk_commando(spelers, speler, 'schoonmaken_verwerken')
            return f'Check!'
        else:
            return feedback
    
    @with_spelers
    @staticmethod
    def schoonmaken_verwerken(spelers, speler, *args):
        spelers[speler]['bedrenkt'] = False
        bedrenkten = [speler_ for speler_ in spelers if spelers[speler_]['bedrenkt']]
        plan_bericht(spelers[speler]['telefoonnummer'], 'De volgende personen zijn bedrenkt:\n- ' + '\n- '.join(bedrenkten), zendtijd(9, 0))
    
    @with_spelers
    @staticmethod
    def aansteken(spelers, speler):
        feedback = basis_feedback(spelers, speler, ['bedrenken', 'schoonmaken', 'aansteken'], 'avond')
        if not feedback:
            bedrenkten = [speler_ for speler_ in spelers if spelers[speler_]['bedrenkt']]
            if len(bedrenkten) == 0:
                return f'Je hebt nog niemand bedrenkt.'
            verwerk_commando(spelers, speler, 'aansteken_verwerken')
            return f'Check!'
        else:
            return feedback
    

    @with_spelers
    @staticmethod
    def aansteken_verwerken(spelers, speler, *args):
        bedrenkten = [speler_ for speler_ in spelers if spelers[speler_]['bedrenkt'] if spelers[speler_]['rol'] != 'plaagkoning' and spelers[speler_]['moloch_kracht'] < 5]
        for bedrenkte in bedrenkten:
            spelers = dood(spelers, speler, bedrenkte, 'verbrand')



class moloch(rol):
    rol =               'moloch'
    aura =              'onbekend'
    bondgenootschap =   'neutralen'
    nachtimmuun =       0

    @with_spelers
    @staticmethod
    def doden(spelers, speler, doelwit):
        feedback = basis_feedback(spelers, speler, ['doden'], 'avond', doelwit)
        if not feedback:
            if spelers[speler]['cooldown'] > 0:
                return f'Je kunt nu nog geen moord plegen.'
            verwerk_commando(spelers, speler, 'doden_verwerken', doelwit)
            return f'Check!'
        else:
            return feedback
        
    @with_spelers
    @staticmethod
    def doden_verwerken(spelers, speler, *args):
        doelwit = args[0] if not spelers[args[0]]['robbie_rotten'] else spelers[args[0]]['robbie_rotten']
        kracht = spelers[speler]['moloch_kracht']

        if spelers[doelwit]['rol'] == 'plaagkoning' and spelers[speler]['moloch_kracht'] == 5:
            plan_bericht(naam_nummer('dorp_app'), 'De grond schudt onder de voeten als een onstopbare kracht op een ondoordringbaar object stuit.')

        elif kracht == 0:
            if spelers[doelwit]['nachtimmuun']:
                spelers[speler]['cooldown'] = 2
                plan_bericht(f'Je doelwit was te sterk!')
            else:
                spelers[speler]['cooldown'] = 0
                spelers = dood(spelers, speler, doelwit, 'moloch_1')
                spelers[speler]['moloch_kracht'] = 1

        elif kracht == 1:
            if spelers[doelwit]['nachtimmuun']:
                plan_bericht(f'Je doelwit was te sterk!')
            else:
                spelers[speler]['nachtimmuun'] = 1
                spelers = dood(spelers, speler, doelwit, 'moloch_2')
                spelers[speler]['moloch_kracht'] = 2
        
        elif kracht == 2:
            if spelers[doelwit]['nachtimmuun']:
                plan_bericht(f'Je doelwit was te sterk!')
            else:
                spelers[speler]['aura'] = 'goed'
                spelers = dood(spelers, speler, doelwit, 'moloch_3')
                spelers[speler]['moloch_kracht'] = 3
        
        elif kracht == 3:
            spelers = dood(spelers, speler, doelwit, 'moloch_4')
            spelers[speler]['moloch_kracht'] = 4
        
        elif kracht >= 4:
            spelers[speler]['nachtimmuun'] = 2
            spelers = dood(spelers, speler, doelwit, 'moloch_5')
            spelers[speler]['moloch_kracht'] = 5
    
    @with_spelers
    @staticmethod
    def status(spelers, speler):
        krachten = {1: 'Je kunt iedere nacht aanvallen.',
                    2: 'Je hebt nachtimmuniteit tegen de wolven, seriemoordenaar en de vigilant.',
                    3: 'Je hebt de aura "goed".',
                    4: 'Je kunt iedereen met nacht-immuniteit vermoorden.',
                    5: 'Je bent immuun tegen alles behalve de executie.'}
        
        kracht = spelers[speler]['moloch_kracht']

        if kracht == 0:
            return f'Je hebt nog geen krachten.'

        krachten_lijst = []
        for x in range(1, kracht + 1):
            krachten_lijst.append(krachten[x])
        
        bericht = 'Je hebt nu de volgende krachten:\n- ' + '\n- '.join(krachten_lijst)
        return bericht



class seriemoordenaar(rol):
    rol =               'seriemoordenaar'
    aura =              'onbekend'
    bondgenootschap =   'neutralen'
    nachtimmuun =       1

    @with_spelers
    @staticmethod
    def doden(spelers, speler, doelwit):
        feedback = basis_feedback(spelers, speler, ['doden'], 'avond', doelwit)
        if not feedback:
            verwerk_commando(spelers, speler, 'doden_verwerken', doelwit)
            return f'Check!'
        else:
            return feedback
    
    @with_spelers
    @staticmethod
    def doden_verwerken(spelers, speler, *args):
        doelwit = args[0] if not spelers[args[0]]['robbie_rotten'] else spelers[args[0]]['robbie_rotten']
        if spelers[doelwit]['nachtimmuun']:
            plan_bericht(spelers[speler]['telefoonnummer'], 'Je doelwit was te sterk!', zendtijd(9, 0))
        else:
            spelers = dood(spelers, speler, doelwit, 'seriemoordenaar')
    


class zwarte_rat(rol):
    rol =               'zwarte_rat'
    aura =              'onbekend'
    bondgenootschap =   'neutralen'
    nachtimmuun =       1

    @with_spelers
    @staticmethod
    def infecteren(spelers, speler, doelwit):
        feedback = basis_feedback(spelers, speler, ['infecteren'], 'avond', doelwit)
        if not feedback:
            verwerk_commando(spelers, speler, 'infecteren_verwerken', doelwit)
            return f'Check!'
        else:
            return feedback

    @with_spelers
    @staticmethod
    def infecteren_verwerken(spelers, speler, *args):
        doelwit = args[0] if not spelers[args[0]]['robbie_rotten'] else spelers[args[0]]['robbie_rotten']

        spelers[doelwit]['geinfecteerd'] = True
        geinfecteerden = [speler_ for speler_ in spelers if spelers[speler_]['geinfecteerd'] and not spelers[speler_]['dood']]

        for geinfecteerde in geinfecteerden:
            for gast in spelers[geinfecteerde]['gasten']:
                spelers[gast]['geinfecteerd'] = True
            
        geinfecteerden = [speler_ for speler_ in spelers if spelers[speler_]['geinfecteerd'] and not spelers[speler_]['dood'] and speler_ != speler]
        
        plan_bericht(spelers[speler]['telefoonnummer'], 'De volgende personen zijn nu geinfecteerd:\n- ' + '\n- '.join(geinfecteerden), zendtijd(9, 0))
    
    @with_spelers
    @staticmethod
    def status(spelers, speler):
        geinfecteerden = [speler_ for speler_ in spelers if spelers[speler_]['geinfecteerd'] and not spelers[speler_]['dood'] and speler_ != speler]
        niet_geinfecteerden = [speler_ for speler_ in spelers if not spelers[speler_]['geinfecteerd'] and not spelers[speler_]['dood'] and speler_ != speler]
        return f'De volgende personen zijn nu geinfecteerd:\n- ' + '\n- '.join(geinfecteerden) + f'\n\nJe moet nog {len(niet_geinfecteerden)} persoon infecteren.'



class stuntman(rol):
    rol =               'stuntman'
    aura =              'onbekend'
    bondgenootschap =   'neutralen'
    nachtimmuun =       1

    @with_spelers
    @staticmethod
    def stunten(spelers, speler, rol):
        feedback = basis_feedback(spelers, speler, ['stunten'], 'stuntman')
        if not feedback:
            stuntman_rollen = [spelers[speler_]['rol'] for speler_ in spelers if spelers[speler_]['stuntman_dood'] == True]
            if rol not in stuntman_rollen:
                return f'Je kunt deze rol niet overnemen.'
            
            doelwit = next((naam for naam, data in spelers.items() if data["rol"] == rol), None)

            for eigenschap in ['rol', 'aura', 'bondgenootschap', 'nachtimmuun', 'kracht_ingezet', 'voorwerp', 'huidig_voorwerp', 'afzetten_ingezet', 'stemming_ingezet', 'stemming_beinvloed', 'gespiekt', 'kogels', 'lijfwacht', 'kans', 'cooldown', 'spuiten', 'zelf_beschermd', 'dag', 'koppel_gemaakt', 'drankjes', 'blinde_gek_doelwit', 'moloch_kracht']:
                spelers[speler][eigenschap] = spelers[doelwit][eigenschap]
            
            plan_bericht(naam_nummer('dorp_app'), f"De stuntman herrinert zich de rol: {rol.replace('_', ' ')}")

            return f"Je hebt de rol {rol.replace('_', ' ')} overgenomen."
        else:
            return feedback
    
    @with_spelers
    @staticmethod
    def status(spelers, speler):
        rollen = [spelers[speler_]['rol'] for speler_ in spelers if spelers[speler_]['stuntman_dood']]
        if len(rollen) > 0:
            return 'De volgende rollen kunnen momenteel worden overgenomen:\n- ' + '\n- '.join(rollen)
        else:
            return 'Er kunnen momenteel geen rollen worden overgenomen.'



class advocaat(rol):
    rol =               'advocaat'
    aura =              'onbekend'
    bondgenootschap =   'neutralen'
    nachtimmuun =       1



class witte_wolf(rol):
    rol =               'witte_wolf'
    aura =              'slecht'
    bondgenootschap =   'neutralen'
    nachtimmuun =       False

    @with_spelers
    @staticmethod
    def doden(spelers, speler, doelwit):
        feedback = basis_feedback(spelers, speler, ['doden'], 'avond')
        if not feedback:
            if int(spelers[speler]['dag'])%2 == 0:
                return f'Je kunt vandaag geen extra moord plegen.'
            verwerk_commando(spelers, speler, 'doden_verwerken', doelwit)
            return f'Check!'
        else:
            return feedback
    
    @with_spelers
    @staticmethod
    def doden(spelers, speler, *args):
        doelwit = args[0] if not spelers[args[0]]['robbie_rotten'] else spelers[args[0]]['robbie_rotten']
        if spelers[doelwit]['nachtimmuun']:
            plan_bericht(spelers[speler]['telefoonnummer'], 'Je doelwit was te sterk!', zendtijd(9, 0))
        elif spelers[doelwit]['locatie'] != doelwit:
            return f'Je doelwit was niet thuis.'
        else:
            spelers = dood(spelers, speler, doelwit, 'wolf')



class piraat(rol):
    rol =               'piraat'
    aura =              'onbekend'
    bondgenootschap =   'neutralen'
    nachtimmuun =       1

    @with_spelers
    @staticmethod
    def plunder(spelers, speler, doelwit, aanval):
        feedback = basis_feedback(spelers, speler, ['plunder'], 'avond', doelwit)
        if not feedback:
            if aanval not in ['kromzwaard', 'rapier', 'pistool']:
                return f'Dit is geen geldige aanval. Kies uit kromzwaard, rapier of pistool.'
            verwerk_commando(spelers, speler, 'plunder_verwerken', doelwit, aanval)
            return f'Check!'
        else:
            return feedback
        
    @with_spelers
    @staticmethod
    def plunder_verwerken(spelers, speler, *args):
        doelwit = args[0] if not spelers[args[0]]['robbie_rotten'] else spelers[args[0]]['robbie_rotten']
        aanval = args[1]

        ## Staat verdediging to van het doelwit
        spelers[speler]['verdediging_toegestaan'] = aanval

        ## Opent commandos.json
        with open('data/commandos.json', 'r') as file:
            commandos = json.load(file)

        ## Schrijft een nieuwe json zonder commandos van het doelwit
        commandos = [entry for entry in commandos if entry['speler'] != doelwit]

        ## Schrijft commandos terug naar bestand
        with open('data/commandos.json', 'w') as file:
            json.dump(commandos, file, indent = 4)
        
        ## Stuurt bericht naar de verdediger
        plan_bericht(spelers[doelwit]['telefoonnummer'], 'Je wordt geplunderd door de piraat! Kies voor 00:00 een verdediging. Dit doe je met /verdedig <opzij/maliënkolder/achteruit>')



class slavendrijver(rol):
    rol =               'slavendrijver'
    aura =              'onbekend'
    bondgenootschap =   'neutralen'
    nachtimmuun =       1

    @with_spelers
    @staticmethod
    def vangen(spelers, speler):
        feedback = basis_feedback(spelers, speler, ['vangen'], 'avond')
        if not feedback:
            verwerk_commando(spelers, speler, 'vangen_verwerken')
            return f'Check!'
        else:
            return feedback

    @with_spelers
    @staticmethod
    def vangen_verwerken(spelers, speler, *args):
        doelwit = args[0] if not spelers[args[0]]['robbie_rotten'] else spelers[args[0]]['robbie_rotten']
        op_straat = [speler_ for speler_ in spelers if spelers[speler_]['op_straat'] and not spelers[speler_]['dood'] and not spelers[speler_]['rol'] == 'slaaf']

        slaven = [speler_ for speler_ in spelers if spelers[speler_]['rol'] == 'slaaf']
        for slaaf in slaven:
            kans = random.randint(1, 5)
            if kans < 4:
                continue
            else:
                spelers[slaaf]['rol'] = spelers[slaaf]['oude_rol']
                plan_bericht(spelers[slaaf]['telefoonnummer'], 'Je bent succesvol ontsnapt aan de slavendrijver en hebt je vrijheid weer terug!', zendtijd(9, 0))

        slaaf = random.choice(op_straat)
        kans = random.randint(1, 5)
        if kans < 4:
            spelers[slaaf]['slaaf'] = True
            plan_bericht(spelers[slaaf]['telefoonnummer'], f'Je bent gevangen genomen als slaaf! Je meester is {speler.capitalize()}', zendtijd(9, 0))
            spelers[speler]['rol'] = 'slaaf'
            spelers[speler]['locatie'] = 'schuur'
        if kans == 4:
            plan_bericht(spelers[slaaf]['telefoonnummer'], 'Je bent gevangen genomen als slaaf, maar je wist succesvol te ontsnappen!', zendtijd(9, 0))
        if kans == 5:
            plan_bericht(spelers[slaaf]['telefoonnummer'], 'Je bent gevangen genomen als slaaf, maar je wist succesvol te ontsnappen en je hebt de dader weten te doden!', zendtijd(9, 0))
            spelers = dood(spelers, doelwit, speler, 'ontsnapping')



class glitch(rol):
    rol =               'glitch'
    aura =              'onbekend'
    bondgenootschap =   'neutralen'
    nachtimmuun =       1

    @with_spelers
    @staticmethod
    def sample(spelers, speler, doelwit):
        feedback = basis_feedback(spelers, speler, ['sample, doden'], 'avond', doelwit)
        if not feedback:
            if doelwit in spelers[speler]['samples']:
                return f'Je hebt deze persoon al in je database staan.'
            verwerk_commando(spelers, speler, 'sample_verwerken', doelwit)
            return f'Check!'
        else:
            return feedback
    
    @with_spelers
    @staticmethod
    def sample_verwerken(spelers, speler, *args):
        doelwit = args[0] if not spelers[args[0]]['robbie_rotten'] else spelers[args[0]]['robbie_rotten']

        spelers[speler]['samples'].append(doelwit)
        plan_bericht(spelers[speler]['telefoonnummer'], 'Het sampelen is gelukt! Dit is je huidige database:\n- ' + '\n- '.join(spelers[speler]['samples']), zendtijd(9, 0))

    @with_spelers
    @staticmethod
    def doden(spelers, speler, doelwit, vermomming):
        feedback = basis_feedback(spelers, speler, ['sample', 'doden'], 'avond', doelwit, vermomming)
        if not feedback:
            database = [speler_ for speler_ in spelers[speler]['samples'] if not spelers[speler_]['dood']]
            if vermomming not in database:
                return f'Je hebt deze persoon niet in je database staan.'
            verwerk_commando(spelers, speler, 'doden_verwerken', doelwit, vermomming)
            return f'Check!'
        else:
            return feedback
        
    @with_spelers
    @staticmethod
    def doden_verwerken(spelers, speler, *args):
        doelwit = args[0] if not spelers[args[0]]['robbie_rotten'] else spelers[args[0]]['robbie_rotten']
        vermomming = args[1]

        if spelers[doelwit]['nachtimmuun']:
            plan_bericht(spelers[speler]['telefoonnummer'], 'Je doelwit was te sterk!', zendtijd(9, 0))
            return

        ## Vermomt de speler als de vermomming
        spelers[speler]['robbie_rotten'] = vermomming

        ## Doodt het doelwit als de vermomming
        spelers = dood(spelers, vermomming, doelwit, 'mes')

        ## Verhoogt het aantal slachtoffers
        spelers[speler]['slachtoffers'] += 1

    @with_spelers
    @staticmethod
    def status(spelers, speler):
        database = [speler_ for speler_ in spelers[speler]['samples'] if not spelers[speler_]['dood']]
        return 'Het sampelen is gelukt! Dit is je huidige database:\n- ' + '\n- '.join(database)



class baltimore(rol):
    rol =               'baltimore'
    aura =              'slecht'
    bondgenootschap =   'wolven'
    nachtimmuun =       False

    @with_spelers
    @staticmethod
    def doden(spelers, speler, doelwit):
        feedback = basis_feedback(spelers, speler, ['doden'], 'avond', doelwit)
        if not feedback:
            if spelers[speler]['kracht_ingezet'] >= 2:
                return f'Je kunt geen extra moorden meer plegen.'
            verwerk_commando(spelers, speler, 'doden_verwerken', doelwit)
            return f'Check!'
        else:
            return feedback
    
    @with_spelers
    @staticmethod
    def doden_verwerken(spelers, speler, *args):
        doelwit = args[0] if not spelers[args[0]]['robbie_rotten'] else spelers[args[0]]['robbie_rotten']
        if spelers[doelwit]['nachtimmuun']:
            plan_bericht(spelers[speler]['telefoonnummer'], 'Je doelwit was te sterk!', zendtijd(9, 0))
        else:
            spelers = dood(spelers, speler, doelwit, 'baltimore')
            spelers[speler]['cooldown'] = 2
        
        spelers[speler]['op_straat'] = True
        spelers[speler]['locatie'] = doelwit



class blockwolf(rol):
    rol =               'blockwolf'
    aura =              'slecht'
    bondgenootschap =   'wolven'
    nachtimmuun =       False

    @with_spelers
    @staticmethod
    def blokkeer(speler, spelers, doelwit):
        ## Genereert algemene feedback
        feedback = basis_feedback(spelers, speler, ['blokkeer'], 'avond', doelwit)
        if not feedback:

            ## Vertelt de speler dat hij/zij zichzelf niet kan blokkeren
            if speler == doelwit:
                return f'Je kunt jezelf niet blokkeren.'
            
            ## Vertelt de speler dat het doelwit niet twee keer achter elkaar dezelfde persoon mag zijn
            if doelwit == spelers[speler]['doelwit']:
                return f'Je kunt niet twee keer achter elkaar dezelfde persoon blokkeren.'
            
            ## Zet het commando in de wacht
            verwerk_commando(spelers, speler, 'blokkeer_verwerken', doelwit)

            ## Geeft feedback
            return 'Check!'
        
        ## Geeft algemene feedback
        else:
            return feedback
    
    @with_spelers
    @staticmethod
    def blokkeer_verwerken(spelers, speler, *args):
        """Verwerkt het commando blokkeer van de blocker. Blokkeert het doelwit, tenzij niet mogelijk.

        Args:
            (spelers) (dict): Alle spelers en hun gegevens
            speler (str): Naam van de speler die het commando uitvoert.
            args (str): Naam van het doelwit.
        """

        ## Bepaalt het doelwit
        doelwit = args[0] if not spelers[args[0]]['robbie_rotten'] else spelers[args[0]]['robbie_rotten']

        ## Zorgt ervoor dat de blocker en blockwolf niet geblokkeerd kunnen worden
        if spelers[doelwit]['rol'] in ['blocker', 'blockwolf']:
            plan_bericht(spelers[doelwit]['telefoonnummer'], 'Iemand probeerde je te blokkeren, maar dat is niet gelukt.', zendtijd(9, 0))
        else:
            ## Opent commandos.json
            with open('data/commandos.json', 'r') as file:
                commandos = json.load(file)

            ## Schrijft een nieuwe json zonder commandos van het doelwit
            commandos = [entry for entry in commandos if entry['speler'] != doelwit]

            ## Schrijft commandos terug naar bestand
            with open('data/commandos.json', 'w') as file:
                json.dump(commandos, file, indent = 4)
            
            ## Stuurt bericht naar doelwit
            plan_bericht(spelers[doelwit]['telefoonnummer'], 'Je bent geblokkeerd.', zendtijd(9, 0))
            spelers[speler]['doelwit'] = doelwit



class coronawolf(rol):
    rol =               'coronawolf'
    aura =              'slecht'
    bondgenootschap =   'wolven'
    nachtimmuun =       False

    @with_spelers
    @staticmethod
    def infecteer(spelers, speler, doelwit):
        feedback = basis_feedback(spelers, speler, ['infecteer'], 'priester', doelwit)
        if not feedback:
            if spelers[speler]['kracht_ingezet']:
                return f'Je hebt deze kracht al ingezet.'
            
            if spelers[doelwit]['bondgenootschap'] == 'wolven' or spelers[doelwit]['rol'] == 'witte_wolf':
                return f'Deze speler is al een wolf'
            
            spelers[speler]['kracht_ingezet'] = True
            if spelers[speler]['rol'] == 'waarzegger' or (spelers[speler]['rol'] == 'moloch' and spelers[speler]['moloch_kracht'] >= 7):
                return f'Check!'
            else:
                spelers[doelwit]['rol'] = 'weerwolf'
                spelers[doelwit]['arua'] = 'slecht'
                spelers[doelwit]['bondgenootschap'] = 'wolven'
                spelers[doelwit]['nachtimmuun'] = False
                return f'Check!'

        else:
            return feedback



class dictatorwolf(rol):
    rol =               'dictatorwolf'
    aura =              'slecht'
    bondgenootschap =   'wolven'
    nachtimmuun =       False

    @with_spelers
    @staticmethod
    def stemming(spelers, speler):
        feedback = basis_feedback(spelers, speler, ['stemming'], 'stemmen')
        if not feedback:

            ## Vertelt de speler dat de stemming niet beïnvloed kan worden op verkiezingsdag
            if not any(spelers[speler_]['burgemeester'] == True for speler_ in spelers):
                return f'Je kunt de stemming de eerste dag niet beïnvloeden.'

            eigen_rechter = next((naam for naam in spelers if spelers[naam]["stemming_ingezet"] == 'eigen_rechter'), None)
            if eigen_rechter:
                return f'Er is al met de stemming geknoeid.'

            spelers[speler]['stemming_beinvloed'] = 'dictatorwolf'
            spelers[speler]['kracht_ingezet'] = True

            gestemden = [speler_ for speler_ in spelers if spelers[speler_]['gestemd']]
            niet_gestemden = [speler_ for speler_ in spelers if speler_ not in gestemden]

            for gestemd in gestemden:
                stem = spelers[gestemd]['gestemd']
                spelers[stem]['stemmen'] += 1000
            
            return f'Check!'
        else:
            return feedback



class spiegelwolf(rol):
    rol =               'spiegelwolf'
    aura =              'slecht'
    bondgenootschap =   'wolven'
    nachtimmuun =       False

    @with_spelers
    @staticmethod
    def dodenlijst(spelers, speler):
        feedback = basis_feedback(spelers, speler, ['doden'], 'nacht')
        if not feedback:
            doden = [speler_ for speler_ in spelers if spelers[speler_]['huidig_dood']]
            if not doden:
                return f'Er sterft vannacht niemand.'
            else:
                return f'De volgende mensen sterven vannacht:\n- ' + '\n- '.join(doden)
        else:
            return feedback
        
    
    @with_spelers
    @staticmethod
    def spiegel(spelers, speler, doelwit):
        feedback = basis_feedback(spelers, speler, ['doden'], 'nacht', doelwit)
        if not feedback:
            if spelers[speler]['kracht_ingezet']:
                return f'Je hebt deze kracht al ingezet.'
            doden = [speler_ for speler_ in spelers if spelers[speler_]['huidig_dood']]
            if doelwit not in doden:
                return f'{doelwit.capitalize()} gaat vannacht niet dood.'
            
            spelers[doelwit]['spiegelwolf'] = True
            spelers[doelwit]['rol'] = 'weerwolf'
            spelers[speler]['kracht_ingezet'] = True
        else:
            return feedback
        


class wolf_in_schaapskleren(rol):
    rol =               'wolf_in_schaapskleren'
    aura =              'goed'
    bondgenootschap =   'wolven'
    nachtimmuun =       False



class beschermende_wolf(rol):
    rol =               'beschermende_wolf'
    aura =              'slecht'
    bondgenootschap =   'wolven'
    nachtimmuun =       False

    @with_spelers
    @staticmethod
    def beschermen(spelers, speler, doelwit):
        feedback = basis_feedback(spelers, speler, ['beschermen'], 'stemmen', doelwit)
        if not feedback:
            spelers[doelwit]['beschermende_wolf'] = speler



class stiltewolf(rol):
    rol =               'stiltewolf'
    aura =              'slecht'
    bondgenootschap =   'wolven'
    nachtimmuun =       False

    @with_spelers
    @staticmethod
    def stilte(spelers, speler, doelwit):
        feedback = basis_feedback(spelers, speler, ['stilte'], 'avond', doelwit)
        if not feedback:
            if spelers[speler]['kracht_ingezet'] >= 3:
                return f'Je kunt deze kracht niet meer inzetten.'
            if spelers[speler]['doelwit'] == 'doelwit':
                return f'Je kunt niet twee keer dezelfde persoon op stil zetten.'
            verwerk_commando(spelers, speler, 'stilte_verwerken', doelwit)
            return f'Check!'
        else:
            return feedback


    @with_spelers
    @staticmethod
    def stilte_verwerken(spelers, speler, *args):
        doelwit = args[0]
        plan_bericht(spelers[doelwit]['telefoonnummer'], 'Je bent op stil gezet! Je mag tot overmorgen 9:00 niet praten en stemmen.')
        spelers[speler]['kracht_ingezet'] += 1



class wijze_wolf(rol):
    rol =               'wijze_wolf'
    aura =              'slecht'
    bondgenootschap =   'wolven'
    nachtimmuun =       False

    @with_spelers
    @staticmethod
    def wel(spelers, speler):
        feedback = basis_feedback(spelers, speler, ['wel', 'niet'], 'avond')
        if not feedback:
            dag = int(spelers[speler]['dag'])
            if dag%2 != 0:
                return f'Je kunt alleen namen krijgen die WEL in het spel zitten op even dagen.'

            rollen = [spelers[speler_]['rol'] for speler_ in spelers if spelers[speler_]['bondgenootschap'] != 'wolven']
            rollen = random.sample(rollen, 2)
            return f'De volgende rollen zitten WEL in het spel:\n- ' + '\n- '.join((rollen))
        else:
            return feedback
    
    @with_spelers
    @staticmethod
    def niet(spelers, speler):
        feedback = basis_feedback(spelers, speler, ['wel', 'niet'], 'avond')
        if not feedback:
            if spelers[speler]['kracht_ingezet']:
                return f'Je hebt deze kracht al ingezet.'
            
            dag = int(spelers[speler]['dag']) + 1

            rollen = [cls.__name__ for cls in rol.__subclasses__()]
            rollen = [rol_.replace('_', ' ').capitalize() for rol_ in rollen if rol_ not in [spelers[speler_]['rol'] for speler_ in spelers]]
            rollen = random.sample(rollen, (4 if dag >= 4 else dag))

            spelers[speler]['kracht_ingezet'] = True

            return f"De volgende {'rollen' if dag > 1 else 'rol'} {'zitten' if dag > 1 else 'zit'} NIET in het spel:\n- " + '\n- '.join((rollen))



class welp(rol):
    rol =               'welp'
    aura =              'slecht'
    bondgenootschap =   'wolven'
    nachtimmuun =       False

    @with_spelers
    @staticmethod
    def doden(spelers, speler, doelwit, rol):
        feedback = basis_feedback(spelers, speler, ['doden'], 'avond', doelwit)
        if not feedback:
            verwerk_commando(spelers, speler, 'doden_verwerken', doelwit, rol)
            return f'Check!'
        else:
            return feedback
    
    @with_spelers
    @staticmethod
    def doden_verwerken(spelers, speler, *args):
        doelwit = args[0] if not spelers[args[0]]['robbie_rotten'] else spelers[args[0]]['robbie_rotten']
        rol = args[1]

        if spelers[doelwit]['nachtimmuun']:
            plan_bericht(spelers[speler]['telefoonnummer'], 'Je doelwit was te sterk!', zendtijd(9, 0))

        spelers[speler]['doelwit'] = doelwit
        spelers[speler]['locatie'] = doelwit
        spelers[speler]['op_straat'] = True

        if spelers[doelwit]['rol'] == rol and not spelers[doelwit]['nachtimmuun']:
            spelers[speler]['rol'] = 'weerwolf'
            spelers = dood(spelers, speler, doelwit, 'welp')



class belastingwolf(rol):
    rol =               'belastingwolf'
    aura =              'slecht'
    bondgenootschap =   'wolven'
    nachtimmuun =       False

    @with_spelers
    @staticmethod
    def doden(spelers, speler, doelwit, rol):
        feedback = basis_feedback(spelers, speler, ['doden'], 'avond', doelwit)
        if not feedback:
            if spelers[speler]['cooldown'] > 0:
                return f'Je kunt nu nog geen moord plegen.'
            verwerk_commando(spelers, speler, 'doden_verwerken', doelwit)
            return f'Check!'
        else:
            return feedback

    @with_spelers
    @staticmethod
    def doden_verwerken(spelers, speler, *args):
        doelwit = args[0] if not spelers[args[0]]['robbie_rotten'] else spelers[args[0]]['robbie_rotten']
        rol = args[1]

        if spelers[doelwit]['nachtimmuun']:
            plan_bericht(spelers[speler]['telefoonnummer'], 'Je doelwit was te sterk!', zendtijd(9, 0))

        if spelers[doelwit]['rol'] == rol:
            spelers[speler]['locatie'] = doelwit
            spelers[speler]['op_straat'] = True
            spelers[speler]['slachtoffers'] += 1
            spelers[speler]['cooldown'] = spelers[speler]['slachtoffers']
            spelers = dood(spelers, speler, doelwit, 'belastingwolf')
        else:
            spelers[speler]['cooldown'] += 1
            spelers[speler]['fouten'] += 1
        
        if spelers[speler]['fouten'] >= 2:
            spelers[speler]['rol'] = 'weerwolf'



class buzzkill(rol):
    rol =               'buzzkill'
    aura =              'slecht'
    bondgenootschap =   'wolven'
    nachtimmuun =       False

    @with_spelers
    @staticmethod
    def buzz(spelers, speler):
        feedback = basis_feedback(spelers, speler, ['buzz'], 'avond')
        if not feedback:
            verwerk_commando(spelers, speler, 'buzz_verwerken')
            return f'Check!'
        else:
            return feedback
        
    @with_spelers
    @staticmethod
    def buzz_verwerken(spelers, speler):
        burgers = [speler_ for speler_ in spelers if spelers[speler_]['bondgenootschap'] == 'burgers']

        ## Opent commandos.json
        with open('data/commandos.json', 'r') as file:
            commandos = json.load(file)

        ## Schrijft een nieuwe json zonder commandos van het doelwit
        commandos = [entry for entry in commandos if entry['speler'] not in burgers]

        ## Schrijft commandos terug naar bestand
        with open('data/commandos.json', 'w') as file:
            json.dump(commandos, file, indent = 4)
        
        spelers[speler]['rol'] = 'weerwolf'



class mijnwolf(rol):
    rol =               'mijnwolf'
    aura =              'slecht'
    bondgenootschap =   'wolven'
    nachtimmuun =       False

    @with_spelers
    @staticmethod
    def graven(spelers, speler, doelwit):
        feedback = basis_feedback(spelers, speler, ['graven_verwerken'], 'avond', doelwit)
        if not feedback:
            if spelers[speler]['kracht_ingezet'] >= 2:
                return f'Je kunt deze kracht niet meer inzetten.'
            verwerk_commando(spelers, speler, 'graven_verwerken', doelwit)
            return f'Check!'
        else:
            return feedback
    
    @with_spelers
    @staticmethod
    def graven_verwerken(spelers, speler, *args):
        doelwit = args[0] if not spelers[args[0]]['robbie_rotten'] else spelers[args[0]]['robbie_rotten']
        if spelers[doelwit]['nachtimmuun']:
            plan_bericht(spelers[speler]['telefoonnummer'], 'Je doelwit was te sterk!', zendtijd(9, 0))
        spelers = dood(spelers, speler, doelwit, 'mijnwolf')