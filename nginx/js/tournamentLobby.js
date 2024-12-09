import { closeTournamentWebsocket } from './websockets.js';
import { textDotLoading } from './animations.js';
import { apiCallAuthed } from './api.js';

export function init(data) {
	// List joined players (refresh every X seconds) - works with /list/player
	fetchAndUpdatePlayerList();
	let refreshInterval = setInterval(fetchAndUpdatePlayerList, 3000);

	// Close the Tournament Websocket and return to main menu
	const returnButton = document.getElementById('cancelBtn');
	if (returnButton) {
		returnButton.addEventListener('click', () => {
			apiCallAuthed(`/api/tournament/join/cancel/${sessionStorage.getItem("tournament_id")}/`, "POST")
				.then(() => {
					console.log('Leaving tournament');
				})
				.catch(error => {
					console.error('Error leaving tournament:', error);
					alert("Error leaving a tournament.");
				})
				.finally(() => {
					closeTournamentWebsocket();
					window.location.hash = '#dashboard';
					clearInterval(refreshInterval);
				})
				;
		});
	}

	// Dot dot dot loading animation
	textDotLoading("loadingAnimation");
}

// List joined players (refresh every X seconds) - works with /list/player
async function fetchAndUpdatePlayerList() {
	try {
		const data = await apiCallAuthed('api/tournament/list/player', undefined, undefined, undefined, false);
		const activeTournament = data[data.length - 1];
		console.log("ACTIVE TOURNAMENT INFO", activeTournament);
		const activePlayers = activeTournament.players;
		const playerListID = document.getElementById("player-list");
		playerListID.innerHTML = '';
		activePlayers.forEach(player => {
			const listItem = document.createElement('li');
			listItem.className = 'list-group-item d-flex justify-content-between align-items-center';
			listItem.innerHTML = `
			${player.player_tmp_username}
			`;
			playerListID.appendChild(listItem);
		});
	} catch (error) {
		console.error('Error fetching player list:', error);
	}
}