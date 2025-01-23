import { closeTournamentWebsocket } from "./websockets.js";
import { textDotLoading } from "./animations.js";
import { apiCallAuthed } from "./api.js";
import { showToast } from "./notifications.js";

let activePlayers = {};

export function init() {
	fetchPlayerList();

	const returnButton = document.getElementById("cancelBtn");
	returnButton.addEventListener("click", cancelLobby);

	// Dot dot dot loading animation
	textDotLoading("loadingAnimation");
}

// Fetch the list of joined players to render the bracket
async function fetchPlayerList() {
	try {
		const data = await apiCallAuthed(`api/tournament/info/${localStorage.getItem("tournament_id")}/`, undefined, undefined, undefined, false);
		console.log("ACTIVE TOURNAMENT INFO", data);

		localStorage.setItem("tournament_capacity", data.capacity);
		activePlayers = data.players;

		renderTournamentBracket(activePlayers, data.capacity);

	} catch (error) {
		console.error("Error fetching player list:", error);
	}
}

// Update the list of joined players via a websocket
export async function handleLobbyStatusUpdate(data) {
	const { player_id, message} = data;
	const userData = await apiCallAuthed(`/api/user/${player_id}/info`);
	const username = userData.username;
	const joinedPlayer = activePlayers.find(player => player.player_tmp_username === username);
	if (message == "player_join" && !joinedPlayer)
		activePlayers.push({ player_tmp_username: username });
	else if (message == "player_cancel" && joinedPlayer)
	{
		const index = activePlayers.findIndex(player => player.player_tmp_username === username);
		if (index !== -1)
			activePlayers.splice(index, 1);
	}
	else if (message == "creator_cancel")
	{
		closeTournamentWebsocket();
		window.location.hash = "#dashboard";
		showToast("Tournament Canceled", "The creator canceled their tournament.", null, "t_tournamentCanceled");
	}
	console.log(activePlayers);
	renderTournamentBracket(activePlayers, localStorage.getItem("tournament_capacity"));
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

			const p1 = activePlayers[match * 2] || { player_tmp_username: "🔜" };
			const p2 = activePlayers[match * 2 + 1] || { player_tmp_username: "🔜" };

			if (round == 1) {
				matchContainer.innerHTML = `
				<div class="player-slot">${p1.player_tmp_username}</div>
				<div class="player-slot">${p2.player_tmp_username}</div>
				`;
			}
			else {
				matchContainer.innerHTML = `
				<div class="player-slot">❓</div>
				<div class="player-slot">❓</div>
				`;
			}

			roundContainer.appendChild(matchContainer);
		}

		bracketContainer.appendChild(roundContainer);
	}
}

// Close the Tournament Websocket and return to main menu
function cancelLobby() {
	apiCallAuthed(`/api/tournament/join/cancel/${localStorage.getItem("tournament_id")}/`, "POST")
		.then(() => {
			console.log("Leaving tournament");
		})
		.catch(error => {
			console.error("Error leaving tournament:", error);
			showToast("Error leaving tournament", null, error, "t_tournamentLeaveError");
		})
		.finally(() => {
			closeTournamentWebsocket();
			window.location.hash = "#dashboard";
		});
}