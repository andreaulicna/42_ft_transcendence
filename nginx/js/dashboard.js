import { textDynamicLoad } from "./animations.js";
import { logout } from "./router.js";
import { apiCallAuthed } from "./api.js";

let logoutBtn;
let stats;

export async function init(data) {
	sessionStorage.setItem("id", data.id);
	
	// Add selected game mode to local storage
	document.querySelectorAll('#menu a').forEach(link => {
		link.addEventListener('click', function() {
			const mode = this.getAttribute('data-mode');
			localStorage.setItem('gameMode', mode);
		});
	});

	// Logout button
	logoutBtn = document.getElementById("logoutButton");
	logoutBtn.addEventListener('click', (event) => {
		event.preventDefault();
		logout();
	});
}