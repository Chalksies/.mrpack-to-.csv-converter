import json
import csv
import os
import requests
import time

index_path = "modrinth.index.json"
with open(index_path, "r", encoding="utf-8") as f:
    data = json.load(f)

mod_list = []
seen_projects = {}

for mod in data["files"]:
    filename = os.path.basename(mod["path"])
    if filename.endswith(".disabled"): 
        jar_name = filename[:-9]  
    else: 
        jar_name = filename
    if filename.endswith(".disabled"): 
        status = "Disabled" 
    else: 
        status = "Enabled"
    mod_name = os.path.splitext(jar_name)[0]

    if not mod["downloads"]:
        mod_list.append((mod_name, status, "N/A"))
        continue

    download_url = mod["downloads"][0]
    try:
        project_id = download_url.split("/data/")[1].split("/")[0]
    except IndexError:
        project_id = None

    if project_id:
        if project_id not in seen_projects:
            try:
                resp = requests.get(f"https://api.modrinth.com/v2/project/{project_id}")
                if resp.ok:
                    seen_projects[project_id] = resp.json()["title"]
                else:
                    seen_projects[project_id] = mod_name
                time.sleep(0.1)  # be nice to the API, don't want to overwhelm it
            except:
                seen_projects[project_id] = mod_name

        pretty_name = seen_projects[project_id]
        modrinth_link = f"https://modrinth.com/mod/{project_id}"
    else:
        pretty_name = mod_name
        modrinth_link = "N/A"

    print("Processed" + pretty_name);
    mod_list.append((pretty_name, status, modrinth_link))

csv_path = "modrinth_mods_pretty.csv"
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Mod Name", "Status", "Modrinth Link"])
    writer.writerows(mod_list)


