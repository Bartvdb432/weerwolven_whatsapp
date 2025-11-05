import csv
import time as time_module
from datetime import datetime, timedelta
import threading
import requests
import tempfile
import os
import pandas as pd



def stuur_bericht(to, message, server_url="http://127.0.0.1:3000/send"):
    payload = {"to": to, "message": message}
    response = requests.post(server_url, json=payload, timeout=10)



def check_berichten(csv_bestand, server_url="http://127.0.0.1:3000/send", check_interval=0.2):
    while True:
        now = time_module.time()
        updated_rows = []

        try:
            with open(csv_bestand, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    ontvanger = row["ontvanger"].strip()
                    bericht = row["bericht"].strip()
                    tijd = float(row["tijd"].strip()) if row['tijd'] != '' else int(time_module.time())

                    if now >= tijd:
                        threading.Thread(
                            target=stuur_bericht,
                            args=(ontvanger, bericht, server_url),
                            daemon=True
                        ).start()
                    else:
                        updated_rows.append(row)

            if updated_rows:
                temp_path = tempfile.mktemp()
                with open(temp_path, 'w', newline='', encoding='utf-8') as tmpfile:
                    writer = csv.DictWriter(tmpfile, fieldnames=["ontvanger", "tijd", "bericht", "mentions"])
                    writer.writeheader()
                    writer.writerows(updated_rows)
                os.replace(temp_path, csv_bestand)
            else:
                with open(csv_bestand, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=["ontvanger", "tijd", "bericht", "mentions"])
                    writer.writeheader()
        except:
            pass

        time_module.sleep(check_interval)



def zendtijd(hour: int, minute: int) -> int:
    now = datetime.now()
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

    if target <= now:
        target += timedelta(days=1)
    
    return time_module.time()
    # return int(target.timestamp())



def plan_bericht(ontvanger: str, bericht: str, tijd: int = None, mentions: list[str] = None):
    import pandas as pd

    tijd = tijd if tijd else int(time_module.time())
    mentions = mentions or []

    # Load existing messages
    try:
        dataframe = pd.read_csv('data/berichten.csv')
    except FileNotFoundError:
        dataframe = pd.DataFrame(columns=['ontvanger', 'bericht', 'tijd', 'mentions'])

    # Prepare the new row
    nieuwe_rij = {
        'ontvanger': ontvanger,
        'bericht': bericht,
        'tijd': tijd,
        'mentions': ",".join(mentions)  # Save as comma-separated string
    }

    # Append and save
    dataframe = pd.concat([dataframe, pd.DataFrame([nieuwe_rij])], ignore_index=True)
    dataframe.to_csv('data/berichten.csv', index=False)