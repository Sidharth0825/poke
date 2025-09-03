# Pokémon Data & Type Effectiveness API

This project uses [PokéAPI](https://pokeapi.co/) to:
1. Fetch Pokémon info from a list (`pokemon1.py`).
2. Run a local server for type effectiveness lookups (`pokemon2.py`).

---

## 📂 Files
- **pokemon.txt** → List of Pokémon names/IDs  
- **pokemon1.py** → Fetches data (ID, name, types, legendary/mythical) from `pokemon.txt` and saves it into `pokemon_data.json`  
- **pokemon2.py** → Starts a local API server for type matchups  
- **pokemon_data.json** → Output Pokémon data  

---

## 🚀 How to Use
1. Install dependencies:
   ```bash
   pip install requests pandas
2. Run the data fetcher:
   python pokemon1.py
→ Creates/updates pokemon_data.json
3. Start the server:
   python pokemon2.py
→ Server runs on http://localhost:8000

## Server Endpoints
?attacker=TYPE&defender=TYPE → Multiplier (e.g., Fire vs Grass)
?attacker=TYPE → Show attacker effectiveness
?defender=TYPE → Show defender resistances/weaknesses
?pokemon=NAME → Pokémon types + weaknesses/resistances

Example:
http://localhost:8000/?attacker=fire&defender=grass
Response:
{ 
  "attacker": "fire", 
  "defender": "grass", 
  "multiplier": 2.0 
}
