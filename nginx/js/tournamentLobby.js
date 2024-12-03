import { closeTournamentWebsocket } from './websockets.js';
import { textDotLoading } from './animations.js';
import { apiCallAuthed } from './api.js';

export function init() {
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
				})
				;
		});
	}

	textDotLoading("loadingAnimation");
}