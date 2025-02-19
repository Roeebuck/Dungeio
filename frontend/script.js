document.addEventListener("DOMContentLoaded", function () {
    console.log("✅ Frontend je propojen!");
});

let storyteller = "";
let playerCount = 1;
let selectedCharacter = "";

// 🔥 Funkce pro spuštění nové hry
async function startNewGame() {
    storyteller = prompt("Jaký bude váš vypravěč?");
    if (!storyteller) {
        alert("❌ Prosím, napište vypravěče!");
        return;
    }

    playerCount = parseInt(prompt("Kolik hráčů bude hrát? (1-6)"));
    if (isNaN(playerCount) || playerCount < 1 || playerCount > 6) {
        alert("❌ Počet hráčů musí být mezi 1 a 6!");
        return;
    }

    // Odeslání na backend pro inicializaci hry
    const response = await fetch("https://dunge-backend.onrender.com/start", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ storyteller, players_count: playerCount })
    });

    const data = await response.json();
    if (data.error) {
        alert("❌ Chyba: " + data.error);
        return;
    }

    displayCharacterSelection(data.characters);
}

// 🔥 Funkce pro výběr postavy
function displayCharacterSelection(characters) {
    const charDiv = document.getElementById("characterSelection");
    charDiv.innerHTML = "<h2>Vyberte si postavu:</h2>";
    charDiv.innerHTML += '<ul class="character-list">' + characters.map((char, index) => `
        <li><button onclick="selectCharacter('${char}')">${index + 1}. ${char}</button></li>
    `).join('') + '</ul>';
    charDiv.style.display = "block";
}

// 🔥 Funkce pro potvrzení výběru postavy
async function selectCharacter(character) {
    selectedCharacter = character;
    
    // Odeslání výběru na backend
    const response = await fetch("https://dunge-backend.onrender.com/choose_character", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ player_id: 1, character_choice: selectedCharacter })
    });

    const data = await response.json();
    if (data.error) {
        alert("❌ Chyba: " + data.error);
        return;
    }

    document.getElementById("characterSelection").style.display = "none";
    document.getElementById("storySection").style.display = "block";
    nextScene();  // Začíná první událost
}

// 🔥 Funkce pro další část příběhu
async function nextScene() {
    const playerInput = document.getElementById("playerInput").value;
    document.getElementById("playerInput").value = "";

    try {
        const response = await fetch("https://dunge-backend.onrender.com/next_event", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                character: selectedCharacter,
                input: playerInput
            })
        });

        const data = await response.json();
        if (data.error) {
            alert("❌ Chyba: " + data.error);
        } else {
            document.getElementById("story").innerText = data.story;
        }
    } catch (error) {
        alert("❌ Chyba připojení k serveru.");
        console.error(error);
    }
}