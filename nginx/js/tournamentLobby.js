import { closeTournamentWebsocket } from './websockets.js';
import { textDotLoading } from './animations.js';
import { apiCallAuthed } from './api.js';

export function init() {
	// List joined players (refresh every X seconds) - works with /list/player
	fetchAndUpdatePlayerList();
	let refreshInterval = setInterval(fetchAndUpdatePlayerList, 3000);

	// Clear the list refresh interval when the user exits the page
	window.addEventListener('hashchange', () => {
		if (window.location.hash !== '#lobby-tnmt') {
			clearInterval(refreshInterval);
		}
	});

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
				});
		});
	}

	// Dot dot dot loading animation
	textDotLoading("loadingAnimation");
}

// List joined players (refresh every X seconds)
async function fetchAndUpdatePlayerList() {
	try {
		const data = await apiCallAuthed(`api/tournament/info/${sessionStorage.getItem("tournament_id")}`, undefined, undefined, undefined, false);
		console.log("ACTIVE TOURNAMENT INFO", data);
		const activePlayers = data.players;
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