import requests
import json
import sys

input_file = r"C:\Sidharth\backend\club_task_2\pokemon.txt"
output_file = sys.argv[1] if len(sys.argv)>1 else r"C:\Sidharth\backend\club_task_2\pokemon_data.json"

with open(input_file, 'r') as f:
    pokemons = [line.strip() for line in f if line.strip()]         # Strips empty lines and whitespace
pokedata ={}
pokemons = list(dict.fromkeys(pokemons))                            # Creates a dictionary where every item of pokemon becomes a key, which is then converted back to a list, as keys cant have duplicates, this removes duplicates
                                                                    #Sets cant be used as they dont maintain order
for p in pokemons:
    url = f"https://pokeapi.co/api/v2/pokemon/{p.lower()}"
    species_url = f"https://pokeapi.co/api/v2/pokemon-species/{p.lower()}"
    try:
        response = requests.get(url)
        response.raise_for_status()             # Checks for HTTP errors
        data = response.json()                  # Coverts to dictionary

        response_species = requests.get(species_url)
        response_species.raise_for_status() 
        species_data = response_species.json()

        poke_info = {
            "id":data["id"],
            "name":data["name"],
            "types":[t["type"]["name"] for t in data["types"]],
            "is_legendary": species_data["is_legendary"],
            "is_mythical": species_data["is_mythical"]
        }
        pokedata[data["name"]] = poke_info
        print(f"Fetched data for {data['name']}")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for {p}: {e}")

with open(output_file, 'w') as f:               # Save results in json file
    json.dump(pokedata, f, indent=4)            # Writes the file in json format
print(f"Data saved to {output_file}")