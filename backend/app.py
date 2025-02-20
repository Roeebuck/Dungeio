import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from game_logic import Game

# ✅ Načtení .env souboru
load_dotenv()

# ✅ Ověření API klíče
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("❌ CHYBA: API klíč nebyl načten! Zkontroluj .env soubor.")

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://www.dunge.io"}})  # Povolení CORS jen pro frontend

game = None  # Herní instance bude inicializována ve start_game

@app.route('/')
def home():
    """Ověření, že backend běží správně"""
    return jsonify({"message": "✅ Backend běží správně!"}), 200

@app.route('/start', methods=['POST'])
def start_game():
    """Inicializace nové hry"""
    global game
    data = request.get_json()

    if not data:
        return jsonify({"error": "❌ Chybějící data!"}), 400
    
    players_count = data.get("players_count")
    storyteller = data.get("storyteller", "").strip()

    if not isinstance(players_count, int) or not (1 <= players_count <= 6):
        return jsonify({"error": "❌ Počet hráčů musí být číslo mezi 1 a 6!"}), 400
    
    if not storyteller:
        return jsonify({"error": "❌ Vypravěč nesmí být prázdný!"}), 400
    
    game = Game(players_count, storyteller)
    response = game.start_game()
    return jsonify(response)

@app.route('/choose_character', methods=['POST'])
def choose_character():
    """Hráči si vybírají postavy"""
    global game
    if game is None:
        return jsonify({"error": "❌ Hra ještě nebyla inicializována!"}), 400

    data = request.get_json()
    if not data:
        return jsonify({"error": "❌ Chybí data!"}), 400
    
    player_id = data.get("player_id")
    character_choice = data.get("character_choice")

    if player_id is None or character_choice is None:
        return jsonify({"error": "❌ player_id a character_choice jsou povinné!"}), 400
    
    response = game.choose_character(player_id, character_choice)
    return jsonify(response)

@app.route('/next_event', methods=['POST'])
def next_event():
    """Generování nové události na základě odpovědí hráčů"""
    global game
    if game is None:
        return jsonify({"error": "❌ Hra ještě nebyla inicializována!"}), 400

    data = request.get_json()
    if not data or "responses" not in data:
        return jsonify({"error": "❌ Chybí data: responses jsou povinné!"}), 400

    player_responses = data["responses"]
    try:
        response = game.process_responses(player_responses)
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": f"❌ Chyba při zpracování odpovědí: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
