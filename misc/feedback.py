import json
from misc.misc import *

@with_commandos
def basis_feedback(commandos, spelers: dict, speler: str, commando: list, tijdstip: str, doelwit: str = None, doelwit_2: str = None):
    dagdelen, tijd = dagdeel(tijdstip)
    if tijdstip not in dagdelen and tijdstip != 'altijd':
        return f'Je kunt deze actie alleen uitvoeren tussen {" en ".join(tijd)}.'
    if any(entry["speler"] == speler and entry["commando"] in [f'{c}_verwerken' for c in commando] for entry in commandos):
        return f'Je mag dit commando niet meer uitvoeren. Gebruik /reset <actie> om dit ongedaan te maken.'
    if spelers[speler]['dood']:
        return f'Je bent al dood.'
    if doelwit != None and doelwit not in spelers:
        return f'Deze speler speelt niet mee of is verkeerd gespeld.'
    if doelwit and spelers.get(doelwit, {}).get('dood'):
        return f'Deze speler is al dood.'
    
    if doelwit_2:
        if doelwit and doelwit_2:
            if any(spelers[speler_]['dood'] for speler_ in [doelwit, doelwit_2]):
                return f'Een van deze spelers is al dood.'
            if spelers[speler]['doelwit'] and any(item in [doelwit, doelwit_2] for item in spelers[speler]['doelwit']):
                return f'Je kunt niet twee keer achter elkaar dezelfde speler verwisselen.'