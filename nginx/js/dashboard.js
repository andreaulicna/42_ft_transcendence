import { openMatchmakingWebsocket } from './websockets.js';

export function init(data) {
	window.searchingPlayerModal = new bootstrap.Modal(document.getElementById('searchingPlayerModal'));
	
	// LOAD DYNAMIC DATA
	document.getElementById('userName').textContent = '🏓 ' + data.username;

	// ADD SELECTED GAME MODE TO LOCAL STORAGE
	document.querySelectorAll('#menu a').forEach(link => {
		link.addEventListener('click', function() {
			const mode = this.getAttribute('data-mode');
			localStorage.setItem('gameMode', mode);

			if (mode === 'remote') {
				openMatchmakingWebsocket();
				searchingPlayerModal.show(); // Open the 'Searching for player' modal
			}
		});
	});

	// Close the 'Searching for player' modal when a match starts
	window.addEventListener('game_redirect', () => {
		if (window.searchingPlayerModal) {
			window.searchingPlayerModal.hide(); // Close the modal when the match starts
		}
	});

}