import { searchForPlayer } from './api.js';

export function init(data) {
	// LOAD DYNAMIC DATA
	document.getElementById('userName').textContent = '🏓 ' + data.user;

	// ADD SELECTED GAME MODE TO LOCAL STORAGE
	document.querySelectorAll('#menu a').forEach(link => {
		link.addEventListener('click', function() {
			const mode = this.getAttribute('data-mode');
			localStorage.setItem('gameMode', mode);

			if (mode === 'remote') {
				searchForPlayer();
			}
		});
	});

}