from google import genai

from misc.verzend import *
from misc.misc import naam_nummer


def genereer_bericht(prompt):
    client = genai.Client(api_key = 'AIzaSyD88SW97V9pXuFr7B40gpvZ8U7KNGYtPUg')
    response = client.models.generate_content(
        model = 'gemini-2.0-flash',
        contents = [prompt])
    
    return response.text



def genereer_startbericht(prompt_pad: str, thema: str, spelers):
    with open('data/prompts/startbericht.txt', 'r') as file:
        tekst = file.read()
    
    tekst = tekst.replace('<THEMA>', thema.capitalize())
    tekst = tekst.replace('<SPELERS>', ', '.join(spelers))

    bericht = genereer_bericht(tekst)
    plan_bericht(naam_nummer('dorp_app'), bericht)