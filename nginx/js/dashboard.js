import { initMatchStartListener } from "./gameCore.js";
import { logout } from "./router.js";

let logoutBtn;

export async function init(id) {
	localStorage.removeItem("match_id");
	if (id !== null) {
		localStorage.setItem("id", id);
	}

	initMatchStartListener();

	// Add selected game mode to local storage
	document.querySelectorAll('#menu .menu-game').forEach(link => {
		link.addEventListener('click', function () {
			const mode = this.getAttribute('data-mode');
			localStorage.setItem('gameMode', mode);
		});
	});

	// Logout button
	logoutBtn = document.getElementById("logoutButton");
	logoutBtn.addEventListener('click', (event) => {
		// event.preventDefault();
		logout();
	});

	// Change animation colors according to user's settings
	const root = document.documentElement;
	const colorLeftPaddle = localStorage.getItem(`${localStorage.getItem("id")}_colorLeftPaddle`) || "#00babc";
	const colorRightPaddle = localStorage.getItem(`${localStorage.getItem("id")}_colorRightPaddle`) || "#df2af7";
	const colorBall = localStorage.getItem(`${localStorage.getItem("id")}_colorBall`) || "whitesmoke";
	root.style.setProperty('--color-left-paddle', colorLeftPaddle);
	root.style.setProperty('--color-right-paddle', colorRightPaddle);
	root.style.setProperty('--color-ball', colorBall);

	// Clean url of URL parameters
	const urlParams = new URLSearchParams(window.location.search);
	if (urlParams.get("access_token"))
	{
		const newUrl = window.location.origin + window.location.pathname + window.location.hash;
		window.history.replaceState({}, document.title, newUrl);
	}
}