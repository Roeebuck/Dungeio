document.addEventListener("DOMContentLoaded", () => {
    console.log("✅ Frontend je propojen!");
});

let storyteller = "";
let playerCount = 1;
let selectedCharacter = "";

const API_BASE_URL = "https://dunge-backend.onrender.com"; // Změň podle potřeby

// 🔥 Funkce pro spuštění nové hry
async function startNewGame() {
    storyteller = prompt("Jaký bude váš vypravěč?");
    if (!storyteller || storyteller.trim() === "") {
        alert("❌ Prosím, napište jméno vypravěče!");
        return;
    }

    let playerInput = prompt("Kolik hráčů bude hrát? (1-6)");
    playerCount = parseInt(playerInput);
    if (isNaN(playerCount) || playerCount < 1 || playerCount > 6) {
        alert("❌ Počet hráčů musí být mezi 1 a 6!");
        return;
    }

    console.log("📤 Odesílám na backend:", JSON.stringify({ storyteller, players_count: playerCount }));

    try {
        const response = await fetch(`${API_BASE_URL}/start`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ storyteller, players_count: playerCount }),
        });

        if (!response.ok) throw new Error(`Server vrátil chybu: ${response.status}`);

        const data = await response.json();
        if (data.error) {
            alert("❌ Chyba: " + data.error);
            return;
        }

        displayCharacterSelection(data.characters);
    } catch (error) {
        alert("❌ Chyba připojení k serveru.");
        console.error("🔴 Chyba:", error);
    }
}

// 🔥 Funkce pro výběr postavy
function displayCharacterSelection(characters) {
    const charDiv = document.getElementById("characterSelection");
    charDiv.innerHTML = "<h2>Vyberte si postavu:</h2>";
    charDiv.innerHTML += `
        <ul class="character-list">
            ${characters.map((char, index) => `<li><button onclick="selectCharacter('${char}')">${index + 1}. ${char}</button></li>`).join('')}
        </ul>
    `;
    charDiv.style.display = "block";
}

// 🔥 Funkce pro potvrzení výběru postavy
async function selectCharacter(character) {
    selectedCharacter = character;
    console.log("📤 Odesílám výběr postavy:", selectedCharacter);

    try {
        const response = await fetch(`${API_BASE_URL}/choose_character`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ player_id: 1, character_choice: selectedCharacter }),
        });

        if (!response.ok) throw new Error(`Server vrátil chybu: ${response.status}`);

        const data = await response.json();
        if (data.error) {
            alert("❌ Chyba: " + data.error);
            return;
        }

        document.getElementById("characterSelection").style.display = "none";
        document.getElementById("storySection").style.display = "block";
        nextScene(); // Spustí první událost
    } catch (error) {
        alert("❌ Chyba připojení k serveru.");
        console.error("🔴 Chyba:", error);
    }
}

// 🔥 Funkce pro další část příběhu
async function nextScene() {
    const playerInput = document.getElementById("playerInput").value.trim();
    document.getElementById("playerInput").value = "";

    if (!playerInput) {
        alert("❌ Musíš něco napsat!");
        return;
    }

    console.log("📤 Odesílám vstup hráče:", playerInput);

    try {
        const response = await fetch(`${API_BASE_URL}/next_event`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                character: selectedCharacter,
                input: playerInput,
            }),
        });

        if (!response.ok) throw new Error(`Server vrátil chybu: ${response.status}`);

        const data = await response.json();
        if (data.error) {
            alert("❌ Chyba: " + data.error);
        } else {
            document.getElementById("story").innerText = data.story;
        }
    } catch (error) {
        alert("❌ Chyba připojení k serveru.");
        console.error("🔴 Chyba:", error);
    }
}