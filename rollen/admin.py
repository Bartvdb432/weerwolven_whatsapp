import random

from misc.misc import *
from rollen.rollen import rol as rol_class

class admin_commandos:
    @with_spelers
    @staticmethod
    def rollen(spelers, speler, verstuur, *deelnemers):
        if speler != 'bart':
            return f'Je bent niet bevoegd om dit commando te gebruiken'
        rollen = [(cls.__name__, cls) for cls in rol_class.__subclasses__()]
        random.shuffle(rollen)

        if len(deelnemers) > len(rollen):
            return f'Er zijn momenteel te weinig rollen toegevoegd voor dit aantal spelers.'

        spelers.clear()  # Clear the old data

        for index, speler_name in enumerate(deelnemers):
            speler_rol = rollen[index]
            spelers[speler_name] = {
                'telefoonnummer': naam_nummer(speler_name),
                'rol': speler_rol[0],
                'aura': speler_rol[1].aura,
                'bondgenootschap': speler_rol[1].bondgenootschap,
                'nachtimmuun': speler_rol[1].nachtimmuun,
                'dood': False,
                'huidig_dood': False,
                'stuntman_dood': False,
                'doodsoorzaak': None,
                'burgemeester': False,
                'tortelduifje': False,
                'roedelleider': False,
                'gedetineerde': False,
                'schild': 0,
                'zwaard': 0,
                'bedrenkt': False,
                'geinfecteerd': False,
                'tijdelijke_rol': None,
                'tijdelijke_aura': None,
                'locatie': speler_name,
                'gasten': [],
                'op_straat': False,
                'doelwit': None,
                'gestemd': None,
                'stemmen': 0,
                'gearresteerd': False,
                'kracht_ingezet': 0,
                'nachtactie': None,
                'voorwerp': None,
                'huidig_voorwerp': None,
                'afzetten_ingezet': False,
                'stemming_ingezet': False,
                'executie_toegestaan': False,
                'stemming_beinvloed': True,
                'gespiekt': False,
                'levensduur': 0,
                'monster': False,
                'tot_leven_gewekt': False,
                'robbie_rotten': None,
                'kogels': 3,
                'zelfmoord': False,
                'lijfwacht_bescherming': None,
                'lijfwacht': 2,
                'kans': 3,
                'cooldown': 0,
                'spuiten': 3,
                'zelf_beschermd': False,
                'dokter_bescherming': None,
                'beschermd': False,
                'vragen': [],
                'dag': 0,
                'koppel_gemaakt': False,
                'drankjes': ['doden', 'helen', 'rol'],
                'blinde_gek_doelwit': [],
                'moloch_kracht': 0,
                'client': None,
                'verdediging_toegestaan': False,
                'slachtoffers': 0,
                'slaaf': False,
                'oude_rol': speler_rol[0],
                'samples': [],
                'spiegelwolf': False,
                'beschermende_wolf': False,
                'simulatiewolf': False,
                'fouten': 0
            }

            if verstuur == 'verstuur':
                plan_bericht(naam_nummer(speler_name), f"_{speler_name.capitalize()}! Jouw rol is {spelers[speler_name]['rol'].replace('_', ' ')}._")

        # Return feedback
        response = '\n'.join([f'{speler_name}: {spelers[speler_name]["rol"]}' for speler_name in deelnemers])

        blinde_gek = next((naam for naam in spelers if spelers[naam]["rol"] == 'blinde_gek'), None)
        if blinde_gek:
            burgers = [s for s in spelers if spelers[s]['bondgenootschap'] == 'burgers' and not spelers[s]['dood']]
            doelwit = random.choice(burgers)
            spelers[blinde_gek]['blinde_gek_doelwit'] = doelwit
            if verstuur == 'verstuur':
                plan_bericht(spelers[blinde_gek]['telefoonnummer'], f'Je doelwit is: {doelwit.capitalize()}.')
        
        advocaat = next((naam for naam in spelers if spelers[naam]["rol"] == 'advocaat'), None)
        if advocaat:
            wolven = [s for s in spelers if spelers[s]['bondgenootschap'] == 'wolven' and not spelers[s]['dood']]
            doelwit = random.choice(wolven)
            spelers[advocaat]['client'] = doelwit
            if verstuur == 'verstuur':
                plan_bericht(spelers[advocaat]['telefoonnummer'], f'Je client is {doelwit.capitalize()}.')
                plan_bericht(spelers[doelwit]['telefoonnummer'], f'Je hebt een advocaat!')


        return response
    


    @staticmethod
    @with_spelers
    def rol(spelers, speler, doelwit, doel_rol):
        ## Checkt bevoegdheid
        if speler != 'bart':
            return f'Je bent niet bevoegd om dit commando te gebruiken'
        
        ## Pakt alle rollen en selecteert de goede
        rollen = {cls.__name__: cls for cls in rol_class.__subclasses__()}
        doel_rol = rollen[doel_rol]

        ## Verandert de data
        spelers[doelwit]['rol'] = doel_rol.__name__
        spelers[doelwit]['aura'] = doel_rol.aura
        spelers[doelwit]['bondgenootschap'] = doel_rol.bondgenootschap
        spelers[doelwit]['nachtimmuun'] = doel_rol.nachtimmuun

        ## Geeft feedback
        return f'De rol van {doelwit.capitalize()} is aangepast naar {doel_rol.__name__}.'



    @staticmethod
    def start(speler, start, thema, *deelnemers):
        from misc.klok import klok
        if speler != 'bart':
            return f'Je bent niet bevoegd om dit commando te gebruiken.'
        thread = threading.Thread(target = klok, args = (speler, start, thema, *deelnemers))
        thread.start()



    @with_spelers
    @staticmethod
    def data(spelers, speler, doelwit, datapunt = None, waarde = None):
        if not datapunt:
            bericht = [f'{doelwit.capitalize()} heeft de volgende data:']
            for key, value in spelers[doelwit].items():
                bericht.append(f'{key}: {value}')
            return '\n'.join(bericht)
        if not waarde:
            bericht = [f'{doelwit.capitalize()} heeft de volgende data bij {datapunt}:',
                       f'{datapunt}: {spelers[doelwit][datapunt]}']
            return '\n'.join(bericht)
        else:
            spelers[doelwit][datapunt] = converteer_string(waarde)
            return f'{datapunt} voor {doelwit.capitalize()} is aangepast naar {waarde}'
    

    @with_spelers
    @staticmethod
    def machtsmisbruik(spelers, speler, doelwit):
        spelers[doelwit]['dood'] = True
        plan_bericht(spelers[doelwit]['telefoonnummer'], f'Je hebt nét iets te tof gedaan tegen {speler.capitalize()}. Je moet dit met het leven bekopen.')



    @staticmethod
    def verwerken(speler):
        with open('data/spelers.json', 'r') as file:
            spelers = json.load(file)

        # Map role class names to classes
        rollen_dict = {cls.__name__: cls for cls in rol_class.__subclasses__()}

        # Load command priorities
        df = pd.read_csv('data/volgorde.csv')
        prioriteiten = {(row['rol'], row['commando']): row['prioriteit'] for _, row in df.iterrows()}

        # Load commands
        with open('data/commandos.json', 'r') as file:
            commandos = json.load(file)

        aantal = len(commandos)

        # Keep track of blocked players
        blocked_players = set()

        # Sort commands by priority (lower first) and FIFO within same priority
        commandos_sorted = sorted(
            commandos,
            key=lambda c: (
                prioriteiten.get((spelers[c['speler']]['rol'], c['commando'].replace('_verwerken','')), 999),
                c['tijd']
            )
        )

        for commando in commandos_sorted:
            speler_name = commando['speler']

            if speler_name in blocked_players:
                continue

            func_name = commando['commando']
            rol = spelers[speler_name]['rol']
            func = getattr(rollen_dict[rol], func_name)

            # If this is a blokkeer command, mark the target as blocked
            if func_name == 'blokkeer_verwerken':
                doelwit = commando['argumenten'][0]
                blocked_players.add(doelwit)

                # Remove all pending commands of the target from memory
                commandos = [c for c in commandos if c['speler'] != doelwit]

            # Execute the command
            func(speler_name, *commando.get('argumenten', []))

            # ✅ Remove the executed command itself from memory
            commandos = [c for c in commandos if c != commando]

        # Save remaining commands back to file
        with open('data/commandos.json', 'w', encoding='utf-8') as file:
            json.dump(commandos, file, indent=4)
        
        return f'{aantal} commando\'s verwerkt.'