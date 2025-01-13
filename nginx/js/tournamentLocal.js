import { apiCallAuthed } from "./api.js";
import { openTournamentWebsocket } from "./websockets.js";
import { showToast } from "./notifications.js";

let tournamentCreateForm;
let tournamentSlots;
let capacity;
let addPlayerBtn;
let players = [];

export function init() {
		tournamentCreateForm = document.getElementById("create-tournament-form");
		tournamentSlots = document.getElementById("tournament-slots");
		addPlayerBtn = document.getElementById("add-player-button");

		renderTournamentBracket();
		addPlayerBtn.addEventListener("click", addPlayerToList);
		tournamentSlots.addEventListener("change", renderTournamentBracket);
		tournamentCreateForm.addEventListener("submit", (e) => createTournament(e));
}

function addPlayerToList() {
	const playerInput = document.getElementById("add-player-form-input");
	const playerName = playerInput.value.trim();
	capacity = parseInt(tournamentSlots.value);

	try {
		if (players.length >= capacity)
		{
			showToast("Error adding player", "The tournament capacity has been filled.");
			throw new Error("The tournament capacity has been filled.");
		}
		if (playerName) {
			players.forEach(player => {
				if (player === playerName)
				{
					showToast("Error adding player", "Players must have unique names.");
					throw new Error("Players must have unique names.");
				}
			});
			players.push(playerName);
			playerInput.value = ""; // Clear the input field
			renderTournamentBracket();
		} else {
			showToast("Error adding player", "Player name cannot be empty.");
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
		heading.innerText = `Round ${round}`;
		roundContainer.appendChild(heading);

		// Number of matches in this round = capacity / 2^round
		const matchesThisRound = capacity / Math.pow(2, round);

		for (let match = 0; match < matchesThisRound; match++) {
			const matchContainer = document.createElement("div");
			matchContainer.className = "match-container";

			let p1 = players[match * 2] || "🔜";
			let p2 = players[match * 2 + 1] || "🔜";

			if (round != 1)
			{
				p1 = "❓";
				p2 = "❓";
			}

			matchContainer.innerHTML = `
				<div class="player-slot">${p1}</div>
				<div class="player-slot">${p2}</div>
			`;
			roundContainer.appendChild(matchContainer);
		}
		bracketContainer.appendChild(roundContainer);
	}
}

// Create a tournament
async function createTournament(event) {
	event.preventDefault();

	const tournamentName = document.getElementById("tournament-name").value;
	const tournamentSlots = document.getElementById("tournament-slots").value;

	try {
		const payload = {
			"tournament_name": tournamentName,
			// "player_tmp_username": "borecek",
		};

		const response = await apiCallAuthed(`/api/tournament/create/${tournamentSlots}/`, "POST", null, payload);
		console.log("TOURNAMENT ID, ", response.tournament.id);
		localStorage.setItem("tournament_id", response.tournament.id);
		openTournamentWebsocket(response.tournament.id);
		window.location.hash = "#lobby-tnmt";
	} catch (error) {
		console.error("Error creating tournament:", error);
		alert("An error occurred while creating a tournament.");
	}
}