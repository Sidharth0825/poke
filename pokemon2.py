import requests
import json
import pandas as pd 
from http.server import BaseHTTPRequestHandler, HTTPServer   # Lets us define how the server respomds, Listens to requests and processes them
from urllib.parse import urlparse, parse_qs   # Helps to break down the URL into components and extract query parameters

BASE = "https://pokeapi.co/api/v2/type/"
POKE_API = "https://pokeapi.co/api/v2/pokemon/"

def get_poke_name(name):                                      # Fetches data for a given pokemon name
    url = f"{POKE_API}{name.lower()}/"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Error fetching data for {name}: {response.status_code}")
    return response.json()

def get_type_data(name):                                      # Fetches data for a given pokemon type
    url = f"{BASE}{name.lower()}/"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Error fetching data for {name}: {response.status_code}")
    return response.json()

def extract_damage_multipliers(data):
    relations = data["damage_relations" ]
    multipliers = {}
    for t in relations["double_damage_from"]:
        multipliers[t["name"]] = 2.0
    for t in relations["half_damage_from"]:
        multipliers[t["name"]] = 0.5
    for t in relations["no_damage_from"]:
        multipliers[t["name"]] = 0.0
    return multipliers

def matrix_build():
    all_types = requests.get(BASE).json()["results"]
    type_names = [t["name"] for t in all_types]
    matrix = {def_type: {} for def_type in type_names if def_type != "unknown"}          # Makes a dictionary with pokemon types as keys and empty values
    for def_type in type_names:
        data = get_type_data(def_type)
        multipliers = extract_damage_multipliers(data)
        matrix[def_type] = {atk_type: multipliers.get(atk_type, 1.0) for atk_type in type_names}
    df = pd.DataFrame(matrix)
    return df
type_matrix = matrix_build()

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):         # Inheritence from BaseHTTPRequestHandler
    def do_GET (self):
        query = parse_qs(urlparse(self.path).query)             # Retrieves the path, breaks and extracts just the query and makes it a dictionary
        attacker = query.get("attacker",[None])[0]              # Gets the value of the key "attacker" from the dictionary, if not found returns None
        defender = query.get("defender",[None])[0]              # Since parse_query returns a list of values for each key, we take the first value
        path = urlparse(self.path).path   
        pokemon = query.get("pokemon",[None])[0]                # Extracts just the path from the URL

        response = {}
        if path == "/matrix":
            response = type_matrix.to_html()          
        elif attacker and defender:
            try:
                multiplier = type_matrix.loc[defender, attacker]  
                response = {
                    "attacker": attacker,
                    "defender": defender,
                    "multiplier": multiplier
                }
            except KeyError:
                response = {"error": "Invalid type name"}
        elif defender:
            row = type_matrix.loc[defender].to_dict()
            response = {
                "defender": defender,
                "multipliers": row         
            }
        elif attacker:
            col = type_matrix[attacker].to_dict()
            response = {
                "attacker": attacker,
                "multipliers": col         
            }
        # row and col are pandas Series objects, which cannot be directly converted to JSON so we convert them to dictionaries
        elif pokemon:
            try:
                poke_data = get_poke_name(pokemon)
                types = [t["type"]["name"] for t in poke_data["types" ]]
                dmg_taken = {
                    atk: type_matrix.loc[atk, types[0]] * (type_matrix.loc[atk, types[1]] if len(types) > 1 else 1.0) 
                    for atk in type_matrix.columns}
                response = {
                    "pokemon": pokemon,
                    "types": types,
                    "damage_taken": dmg_taken
                }
                if len(types) == 1:
                    weak_to = [atk for atk, mult in dmg_taken.items() if mult ==2.0]
                    resistant_to = [atk for atk, mult in dmg_taken.items() if mult ==0.5]
                    immune_to = [atk for atk, mult in dmg_taken.items() if mult ==0.0]
                    
                    response["2x weak to"] = weak_to
                    response["1/2x resistant to"] = resistant_to
                    response["immune to"] = immune_to
                elif len(types) == 2:
                    weak_2x = [atk for atk, mult in dmg_taken.items() if mult == 2.0]
                    weak_4x = [atk for atk, mult in dmg_taken.items() if mult == 4.0]
                    resistant_2x = [atk for atk, mult in dmg_taken.items() if mult == 0.5]
                    resistant_4x = [atk for atk, mult in dmg_taken.items() if mult == 0.25]
                    immune_to = [atk for atk, mult in dmg_taken.items() if mult == 0.0]

                    response["2x weak to"] = weak_2x
                    response["4x weak to"] = weak_4x
                    response["1/2x resistant to"] = resistant_2x
                    response["1/4x resistant to"] = resistant_4x
                    response["immune to"] = immune_to

            except Exception as e:
                response = {"error": str(e)}
        else:
            response = {"error": "Please provide at least an attacker or defender type"}
        
        self.send_response(200)                                             # Tells the client that the request was successful
        self.send_header("Content-Type", "application/json")                # Tells the client that the body of the response is in JSON format
        self.end_headers()
        self.wfile.write(json.dumps(response, indent=4).encode("utf-8"))      # Converts the response dictionary to a JSON string and encodes it to bytes
        
if __name__ == "__main__":
    server = HTTPServer(("localhost", 8000), SimpleHTTPRequestHandler)
    print(type_matrix)
    print("Starting server on http://localhost:8000")
    server.serve_forever()


