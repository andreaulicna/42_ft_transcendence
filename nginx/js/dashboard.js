import { openMatchmakingWebsocket } from './websockets.js';

export function init(data) {
	initializeModals();
	
	// LOAD DYNAMIC DATA
	document.getElementById('userName').textContent = '🏓 ' + data.username;

	// ADD SELECTED GAME MODE TO LOCAL STORAGE
	document.querySelectorAll('#menu a').forEach(link => {
		link.addEventListener('click', function() {
			const mode = this.getAttribute('data-mode');
			localStorage.setItem('gameMode', mode);

			if (mode === 'remote') {
				openMatchmakingWebsocket();
			}
		});
	});

}

export function initializeModals() {
	// Initialize the modal instance after the DOM is fully loaded
	window.searchingPlayerModal = new bootstrap.Modal(document.getElementById('searchingPlayerModal'));
}