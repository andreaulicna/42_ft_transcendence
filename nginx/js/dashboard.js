import { textDynamicLoad } from "./animations.js";

export function init(data) {
	sessionStorage.setItem("id", data.id);

	// LOAD DYNAMIC DATA
	textDynamicLoad("userName", `🏓 ${data.username}`);
	if (data.avatar != null)
		document.getElementById('profilePic').src = data.avatar;

	// ADD SELECTED GAME MODE TO LOCAL STORAGE
	document.querySelectorAll('#menu a').forEach(link => {
		link.addEventListener('click', function() {
			const mode = this.getAttribute('data-mode');
			localStorage.setItem('gameMode', mode);

			// The below part is redundant? Commented out for now
			// if (mode === 'remote') {
			// 	window.location.hash = '#lobby-game';
			// }
		});
	});
}