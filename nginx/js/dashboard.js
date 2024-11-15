import { searchForPlayer } from './api.js';

export function init(data) {
	// DEBUG
	console.log('Dashboard init data:', data);
	// console.log('Username:', data.username);
	
	// LOAD DYNAMIC DATA
	document.getElementById('userName').textContent = '🏓 ' + data.username;

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