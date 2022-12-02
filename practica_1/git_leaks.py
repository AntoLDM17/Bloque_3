#usr/bin/python
import pandas as pd
from git import Repo
import re, signal, sys, json, requests

DIRECTORY = "./skale/skale-manager"

def extract(url):
    try:
        repo = Repo(url)
    except:
        print("[!] Error cloning the repository")
        sys.exit(1)
    
    commits = list(repo.iter_commits())
    return commits

def transform(commits):

    lista_commits = [commit for commit in commits if re.findall("password|PASSWORD|Password|pass|PASS|Pass|key|KEY|Key|secret|SECRET|Secret|watchword|WATCHWORD|Watchword", commit.message)]
    lista_coincidencias = [re.findall("password|PASSWORD|Password|pass|PASS|Pass|key|KEY|Key|secret|SECRET|Secret|watchword|WATCHWORD|Watchword", commit.message) for commit in commits if re.findall("password|PASSWORD|Password|pass|PASS|Pass|key|KEY|Key|secret|SECRET|Secret|watchword|WATCHWORD|Watchword", commit.message)]

    return lista_commits, lista_coincidencias

def load(lista_commits, lista_coincidencias):
    for i in range(len(lista_commits)):
        print("Found", lista_coincidencias[i],"in commit number",i,":\n"+lista_commits[i].message+"\n")

    #Creamos el json
    json_leaks = {}
    for i in range(len(lista_commits)):
        json_leaks[i] = {
            "leak": lista_coincidencias[i],
            "commit": lista_commits[i].message
        }
    #Guardamos el json
    with open('leaks.json', 'w') as outfile:
        json.dump(json_leaks, outfile)


#Ctrl+C
def handler_signal(signal, frame):
    print("[!] Exiting...")
    sys.exit(1)

signal.signal(signal.SIGINT, handler_signal)
        
if __name__ == '__main__':
    commits = extract(DIRECTORY)
    lista_commits, lista_coincidencias = transform(commits)
    load(lista_commits, lista_coincidencias)

    