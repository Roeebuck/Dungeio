import random
import requests
import os
import json
from dotenv import load_dotenv

# Načtení .env souboru
load_dotenv()

# API klíč pro OpenRouter AI
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

if not OPENROUTER_API_KEY:
    raise ValueError("Chybí API klíč! Nastav OPENROUTER_API_KEY v .env nebo na serveru.")

class Game:
    def __init__(self, num_players, storyteller_name):
        self.num_players = num_players
        self.storyteller_name = storyteller_name
        self.players = {}  # Uloží hráče a jejich postavy
        self.characters = {}  # Uchovává seznam vygenerovaných postav
        self.history = []   # Udržuje názvy událostí
        self.round = 0      # Aktuální kolo hry
    
    def generate_characters(self):
        """Generuje 4 postavy pro každého hráče na základě jména vypravěče."""
        for player in range(1, self.num_players + 1):
            response = self.ask_ai(f"Vytvoř 4 unikátní fantasy postavy pro hráče {player} ve světě inspirovaném {self.storyteller_name}.")
            self.characters[player] = response.split('\n')[:4]  # Prvních 4 postav
        return self.characters
    
    def assign_character(self, player_id, character_name):
        """Přiřadí hráči vybranou postavu, pokud existuje."""
        available_characters = sum(self.characters.values(), [])  # Seznam všech dostupných postav
        if character_name not in available_characters:
            return {"error": f"Postava '{character_name}' neexistuje. Vyber z dostupných: {available_characters}"}
        
        self.players[player_id] = character_name
        return {"message": f"Hráč {player_id} si vybral postavu {character_name}."}
    
    def generate_event(self):
        """Generuje úvodní událost na základě vypravěče a postav."""
        prompt = f"Vytvoř úvodní scénu pro příběh inspirovaný {self.storyteller_name}. Hlavní postavy: {', '.join(self.players.values())}."
        response = self.ask_ai(prompt)
        self.history.append(response.split(". ")[0])  # Uloží název první věty jako historii
        return response
    
    def process_turn(self, player_inputs):
        """Zpracovává odpovědi hráčů, generuje nové události a boduje."""
        self.round += 1
        prompt = f"Pokračuj v příběhu. Hráči odpověděli: {player_inputs}. Historie: {', '.join(self.history[-5:])}"
        response = self.ask_ai(prompt)
        self.history.append(response.split(". ")[0])
        return response, self.calculate_scores(player_inputs)
    
    def calculate_scores(self, player_inputs):
        """Ohodnotí odpovědi hráčů pomocí AI."""
        prompt = f"Ohodnoť odpovědi hráčů od 1 do 10 podle jejich kreativity a relevance: {player_inputs}"
        response = self.ask_ai(prompt)
        
        scores = {}
        try:
            scores = json.loads(response)  # AI by měla vrátit JSON se skóre
        except json.JSONDecodeError:
            scores = {player: random.randint(1, 10) for player in player_inputs}  # Záložní metoda
        
        return scores
    
    def ask_ai(self, prompt):
        """Odešle prompt na AI a vrátí odpověď, pokud selže, vrátí výchozí zprávu."""
        headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
        payload = {"model": "gryphe/mythomax-l2-13b", "messages": [{"role": "user", "content": prompt}]}
        
        try:
            response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload)
            response.raise_for_status()
            ai_response = response.json().get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            return ai_response if ai_response else "AI nic neodpověděla, ale dobrodružství pokračuje..."
        except requests.exceptions.RequestException as e:
            return f"Chyba API: {e}. Pokračujte podle svého uvážení!"

# --- Příklad použití ---
if __name__ == "__main__":
    game = Game(num_players=3, storyteller_name="Opilý Gandalf")
    characters = game.generate_characters()
    print("Vygenerované postavy:", characters)
    game.assign_character(1, characters[1][0])
    game.assign_character(2, characters[2][1])
    game.assign_character(3, characters[3][2])
    event = game.generate_event()
    print("Úvodní událost:", event)
    responses, scores = game.process_turn({1: "Jdu do lesa", 2: "Zkoumám jeskyni", 3: "Utíkám pryč"})
    print("Nová událost:", responses, "Body:", scores)