export function init(data) {
	sessionStorage.setItem("id", data.id);

	// LOAD DYNAMIC DATA
	document.getElementById('userName').textContent = '🏓 ' + data.username;

	// ADD SELECTED GAME MODE TO LOCAL STORAGE
	document.querySelectorAll('#menu a').forEach(link => {
		link.addEventListener('click', function() {
			const mode = this.getAttribute('data-mode');
			localStorage.setItem('gameMode', mode);

			if (mode === 'remote') {
				window.location.hash = '#searching';
			}
		});
	});
}