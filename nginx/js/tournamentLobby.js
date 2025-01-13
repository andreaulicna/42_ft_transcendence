import { closeTournamentWebsocket } from "./websockets.js";
import { textDotLoading } from "./animations.js";
import { apiCallAuthed } from "./api.js";

export function init() {
	// List joined players (refresh every X seconds) - works with /list/player
	fetchAndUpdatePlayerList();
	let refreshInterval = setInterval(fetchAndUpdatePlayerList, 3000);

	// Clear the list refresh interval when the user exits the page
	window.addEventListener("hashchange", () => {
		if (window.location.hash !== "#lobby-tnmt") {
			clearInterval(refreshInterval);
		}
	});

	// Close the Tournament Websocket and return to main menu
	const returnButton = document.getElementById("cancelBtn");
	if (returnButton) {
		returnButton.addEventListener("click", () => {
			apiCallAuthed(`/api/tournament/join/cancel/${localStorage.getItem("tournament_id")}/`, "POST")
				.then(() => {
					console.log("Leaving tournament");
				})
				.catch(error => {
					console.error("Error leaving tournament:", error);
					alert("Error leaving a tournament.");
				})
				.finally(() => {
					closeTournamentWebsocket();
					window.location.hash = "#dashboard";
				});
		});
	}

	// Dot dot dot loading animation
	textDotLoading("loadingAnimation");
}

function renderTournamentBracket(activePlayers, capacity) {
	const bracketContainer = document.getElementById("bracket-container");
	bracketContainer.innerHTML = ""; // Clear previous brackets
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

			const p1 = activePlayers[match * 2] || { player_tmp_username: "🔜" };
			const p2 = activePlayers[match * 2 + 1] || { player_tmp_username: "🔜" };

			if (round != 1)
			{
				p1.player_tmp_username = "❓";
				p2.player_tmp_username = "❓";
			}

			matchContainer.innerHTML = `
				<div class="player-slot">${p1.player_tmp_username}</div>
				<div class="player-slot">${p2.player_tmp_username}</div>
			`;

			roundContainer.appendChild(matchContainer);
		}

		bracketContainer.appendChild(roundContainer);
	}
}

// Update fetchAndUpdatePlayerList to render the bracket
async function fetchAndUpdatePlayerList() {
	try {
		const data = await apiCallAuthed(`api/tournament/info/${localStorage.getItem("tournament_id")}`, undefined, undefined, undefined, false);
		console.log("ACTIVE TOURNAMENT INFO", data);

		localStorage.setItem("tournament_capacity", data.capacity);
		const activePlayers = data.players;

		renderTournamentBracket(activePlayers, data.capacity);

	} catch (error) {
		console.error("Error fetching player list:", error);
	}
}