from flask import Flask, request, jsonify, Response
import requests, schedule, time as time_module, threading
from datetime import datetime, time
import os
import yaml
import Levenshtein
import re
import pandas as pd
import heapq
from queue import Queue
from apscheduler.schedulers.background import BackgroundScheduler
import inspect
from threading import Thread

from misc.misc import *
from rollen.algemeen import *
from rollen.rollen import *
from rollen.admin import *
from misc.verzend import *

with open("data/commandos.txt", "r", encoding="utf-8") as file:
    commandos = file.read().splitlines()

admins = ['bart']

app = Flask(__name__)

@app.post("/process")
def process_command():
    data: dict = request.get_json()
    command: str = data.get("command", "").strip()
    private_id: str = data.get("private_id", "")
    group_specific_id: str = data.get("from", "")
    group_id: str = data.get("group_id", "")

    parts: list = command.split()
    cmd: str = parts[0].lower().replace('/', '')
    args: list = [x.lower() for x in parts[1:]]
    speler: str = nummer_naam(private_id)

    args = [re.sub(r'\s+', ' ', ' '.join(args)).strip()] if cmd in ['help', 'antwoorden'] else args
    if cmd == 'vragen':
        joined = re.sub(r'\s+', ' ', ' '.join(args)).strip()
        parts = joined.split(' ', 1)
        args = tuple(parts)

    with open('data/spelers.json', 'r') as file:
        spelers = json.load(file)

    rollen_dict = {cls.__name__: cls for cls in rol.__subclasses__()}
    speler_rol = rollen_dict.get(spelers[speler]['rol'])

    rol_commando_dict = {
        name: getattr(speler_rol, name)
        for name in dir(speler_rol)
        if not name.startswith("__") and callable(getattr(speler_rol, name))
    }

    algemene_commando_dict = {
        name: getattr(algemene_commandos, name)
        for name in dir(algemene_commandos)
        if not name.startswith("__") and callable(getattr(algemene_commandos, name))
    }

    admin_commando_dict = {
        name: getattr(admin_commandos, name)
        for name in dir(admin_commandos)
        if not name.startswith("__") and callable(getattr(admin_commandos, name))
    }

    # --- Rol specifieke commando's ---
    if cmd in rol_commando_dict:
        func = rol_commando_dict[cmd]
        argument = argumenten(func, args)
        if argument:
            return {'reply': argument}
        response = func(speler, *args)
        return {'reply': response}

    elif cmd in algemene_commando_dict:
        func = algemene_commando_dict[cmd]
        argument = argumenten(func, args)
        if argument:
            return {'reply': argument}

        if cmd == "stem" and len(args) >= 1:
            kandidaat = args[0]
            response = func(
                speler=speler,
                kandidaat=kandidaat,
                group_specific_id=group_specific_id,
                group_id=group_id
            )
            # Forward directly to Node.js
            if isinstance(response, dict):
                return response  # contains "react": "✅"
            else:
                return {"reply": response}  # any string feedback
        
        elif cmd == 'dobbel':
            response = func(
                speler = speler,
                group_specific_id = group_specific_id,
                group_id = group_id
            )
            # Forward directly to Node.js
            if isinstance(response, dict):
                return response  # contains "react": "✅"
            else:
                return {"reply": response}  # any string feedback

        elif cmd == 'stemmen':
            response = func(
                arg = args[0],
                speler = speler,
                group_specific_id = group_specific_id,
                group_id = group_id
            )
            # Forward directly to Node.js
            if isinstance(response, dict):
                return response  # contains "react": "✅"
            else:
                return {"reply": response}  # any string feedback
        
        elif cmd == 'radje':
            kwargs = {
                "group_specific_id": group_specific_id,
                "group_id": group_id
            }
            response = func(
                speler, *args, **kwargs
            )
            # Forward directly to Node.js
            if isinstance(response, dict):
                return response  # contains "react": "✅"
            else:
                return {"reply": response}  # any string feedback

        else:
            # Execute all other general commands normally
            response = func(speler, *args)
            return {"reply": response}
    
    elif cmd in admin_commando_dict:
        if speler not in admins:
            return {'reply': 'Dit is een admin commando.'}
        func = admin_commando_dict[cmd]
        argument = argumenten(func, args)
        if argument:
            return {'reply': argument}
        response = func(speler, *args)
        return {'reply': response}
            

    # --- Spellingcontrole ---
    elif cmd not in commandos:
        return {'reply': spelling(cmd, commandos)}
    
    else:
        return {'reply': 'Je bent niet bevoegd om dit commando te gebruiken'}

if __name__ == "__main__":
    Thread(target=check_berichten, args=("data/berichten.csv",), daemon=True).start()
    app.run(host="0.0.0.0", port=5000)