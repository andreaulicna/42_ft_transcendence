import { apiCallAuthed } from "./api.js";
import { openLocalTournamentWebsocket } from "./websockets.js";
import { showToast } from "./notifications.js";

let tournamentCreateForm;
let tournamentSlots;
let capacity;
let addPlayerBtn;
let addPlayerInput;
let players = [];

export function init() {
		tournamentCreateForm = document.getElementById("create-tournament-form");
		tournamentSlots = document.getElementById("tournament-slots");
		addPlayerBtn = document.getElementById("add-player-button");
		addPlayerInput = document.getElementById("add-player-form-input");

		// Clear players array on page load
		players = [];

		renderTournamentBracket();
		addPlayerBtn.addEventListener("click", addPlayerToList);
		tournamentSlots.addEventListener("change", renderTournamentBracket);
		tournamentCreateForm.addEventListener("submit", (e) => createTournament(e));
}

function addPlayerToList() {
	const playerName = addPlayerInput.value.trim();
	capacity = parseInt(tournamentSlots.value);

	// Manually trigger validation
	if (!addPlayerInput.checkValidity()) {
		addPlayerInput.reportValidity();
		return;
	}

	try {
		if (players.length >= capacity)
		{
			showToast("Error adding player", "The tournament capacity has been filled.", null, "t_capacityFilled");
			throw new Error("The tournament capacity has been filled.");
		}
		if (playerName) {
			players.forEach(player => {
				if (player === playerName)
				{
					showToast("Error adding player", "Players must have unique names.", null, "t_uniqueNames");
					throw new Error("Players must have unique names.");
				}
			});
			players.push(playerName);
			addPlayerInput.value = ""; // Clear the input field
			renderTournamentBracket();

			// Temporarily disable the required attribute on the 'Add Player' input so the form can submit
			if (players.length == capacity)
				addPlayerInput.required = false;
		} else {
			showToast("Error adding player", "Player name cannot be empty.", null, "t_emptyName");
			throw new Error("Player name cannot be empty.");
		}
	} catch (error) {
		console.error(error.message);
	};
	
}

function renderTournamentBracket() {
	capacity = parseInt(tournamentSlots.value);
	const bracketContainer = document.getElementById("bracket-container");
	bracketContainer.innerHTML = "";
	bracketContainer.classList.add("d-flex", "justify-content-center", "align-items-center", "bracket-style");

	const totalRounds = Math.log2(capacity);

	for (let round = 1; round <= totalRounds; round++) {
		const roundContainer = document.createElement("div");
		roundContainer.className = "round-container";

		const heading = document.createElement("h5");
		const roundText = document.createElement("span");
		roundText.setAttribute("data-translate", "round");
		roundText.innerText = "Round";
		heading.appendChild(roundText);
		heading.appendChild(document.createTextNode(` ${round}`));
		roundContainer.appendChild(heading);

		// Number of matches in this round = capacity / 2^round
		const matchesThisRound = capacity / Math.pow(2, round);

		for (let match = 0; match < matchesThisRound; match++) {
			const matchContainer = document.createElement("div");
			matchContainer.className = "match-container";

			let p1 = players[match * 2] || "🔜";
			let p2 = players[match * 2 + 1] || "🔜";

			if (round == 1) {
				matchContainer.innerHTML = `
				<div class="player-slot">${p1}</div>
				<span>⚔️</span>
				<div class="player-slot">${p2}</div>
				`;
			}
			else {
				matchContainer.innerHTML = `
				<div class="player-slot">❓</div>
				<span>⚔️</span>
				<div class="player-slot">❓</div>
				`;
			}
			roundContainer.appendChild(matchContainer);
		}
		bracketContainer.appendChild(roundContainer);
	}
}

// Create a tournament
async function createTournament(event) {
	event.preventDefault();

	const tournamentName = document.getElementById("tournament-name").value;

	if (players.length < capacity)
	{
		showToast("Error creating tournament", `Not enough players added.`, null, "t_notEnoughPlayers");
		return;
	}

	try {
		const payload = {
			"tournament_name" : tournamentName,
			"players" : players.slice(0, capacity),
		};

		const response = await apiCallAuthed(`/api/tournament/local/create/${capacity}/`, "POST", null, payload);
		// console.log("TOURNAMENT INFO, ", response);
		localStorage.setItem("tournament_id", response.local_tournament.id);
		openLocalTournamentWebsocket(response.local_tournament.id);
	} catch (error) {
		console.error("Error creating tournament:", error);
		showToast("Error creating tournament", null, error, "t_tournamentError");
	}
}