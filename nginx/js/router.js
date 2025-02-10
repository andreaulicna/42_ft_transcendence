import { showLoading } from "./animations.js";
import { apiCallAuthed, ensureValidAccessToken, refreshAccessToken } from './api.js';
import { hideLoading } from "./animations.js";
import { openStatusWebsocket, openTournamentWebsocket, closeLocalTournamentWebsocket, closeTournamentWebsocket, closeLocalWebsocket, closeRematchWebsocket, closePongWebsocket, closeAIPlayWebsocket, closeMatchmakingWebsocket } from './websockets.js';
import { showToast } from "./notifications.js";

const dynamicContent = document.getElementById('dynamicContent');

const routes = {
	''				: '/pages/login.html',
	'#login'		: '/pages/login.html',
	'#2fa'			: '/pages/2fa.html',
	'#register'		: '/pages/register.html',
	'#dashboard'	: '/pages/dashboard.html',
	'#lobby-game'	: '/pages/gameLobby.html',
	'#game'			: '/pages/game.html',
	'#local-tnmt'	: '/pages/tournamentLocal.html',
	//'#remote-tnmt'	: '/pages/tournamentRemote.html',
	'#lobby-tnmt'	: '/pages/tournamentLobby.html',
	'#winner-tnmt'	: '/pages/tournamentWinner.html',
	'#profile'		: '/pages/profile.html',
	'404'			: '/pages/404.html',
};

const loadContent = async (path) => {
	try {
		showLoading();

		// Load the HTML content
		const response = await fetch(path);
		const content = await response.text();
		dynamicContent.innerHTML = content;

		// Wait for the dynamic content to be fully parsed and available in the DOM -- redundant?
		await new Promise((resolve) => {
			const checkContentLoaded = () => {
				if (dynamicContent.children.length > 0) {
					resolve();
					// console.log("dynamic HTML content loaded!");
				} else {
					setTimeout(checkContentLoaded, 50);
				}
			};
			checkContentLoaded();
		});

		// Reapply language settings after loading new content
		const preferredLanguage = localStorage.getItem("language") || "en";
		setLanguage(preferredLanguage);

		// Import the page's relevant script
		let data;
		if (window.location.hash === '#login' || window.location.hash === '') {
			await import('/js/login.js').then(module => module.init());
		} else if (window.location.hash === '#register') {
			await import('/js/register.js').then(module => module.init());
		} else if (window.location.hash === '#dashboard') {
			// to prevent duplicate calls to api/user/info on load event
			if (localStorage.getItem('id') == null) {
				data = await apiCallAuthed('/api/user/info');
				await import('/js/dashboard.js').then(module => module.init(data.id));
			} else {
				await import('/js/dashboard.js').then(module => module.init(null));
			}
		} else if (window.location.hash === '#profile') {
			data = await apiCallAuthed('/api/user/info');
			await import('/js/profile.js').then(module => module.init(data));
		} else if (window.location.hash === '#lobby-game') {
			await import('/js/gameLobby.js').then(module => module.init());
		} else if (window.location.hash === '#game') {
			const mode = localStorage.getItem('gameMode');
			// console.log("Mode in router", mode);
			if (mode == "local" || mode == "local-rematch" || mode == "local-rematch-switch")
				await import('/js/gameLocal.js').then(module => module.init());
			else if (mode == "ai")
				await import('/js/gameAI.js').then(module => module.init());
			else if (mode == "remote")
				await import('/js/gameRemote.js').then(module => module.init());
			else if (mode == "rematch")
				await import('/js/gameRemote.js').then(module => module.init());
			else if (mode == "tournamentLocal")
				await import('/js/gameTournamentLocal.js').then(module => module.init());
			else if (mode == "tournamentRemote")
				await import('/js/gameTournamentRemote.js').then(module => module.init());
	//	} else if (window.location.hash === '#remote-tnmt') {
	//		await import('/js/tournamentRemote.js').then(module => module.init());
		} else if (window.location.hash === '#local-tnmt') {
			await import('/js/tournamentLocal.js').then(module => module.init());
		} else if (window.location.hash === '#lobby-tnmt') {
			let tournament_id = localStorage.getItem("tournament_id")
			openTournamentWebsocket(tournament_id);
			await import('/js/tournamentLobby.js').then(module => module.init());
		} else if (window.location.hash === '#2fa') {
			await import('/js/2fa.js').then(module => module.init());
		}
	} catch (err) {
		console.error('Error loading content:', err);
	} finally {
		hideLoading();
	}
};

const router = async () => {
	if (appState.isLoggingOut)
		return;

	// Refreshes access token before getting to further API calls, preventing double refresh on load/hashchange events
	appState.loggedIn = await refreshAccessToken();


	// If user is not logged in, redirect them to #login
	if ((window.location.hash != '#login' && window.location.hash != '#2fa' && window.location.hash != '#register' && window.location.hash != '404') && !appState.loggedIn) {
		window.location.hash = '#login';
		// console.log('Not logged in. Redirecting to login.');
		return;
	}

	// If user is logged in, go straight to #dashboard
	if ((window.location.hash === '' || window.location.hash === '#login' || window.location.hash === '#register' ) && appState.loggedIn) {
		window.location.hash = '#dashboard';
		return;
	}

	// Disable manual access to certain pages
	if (window.location.hash === "#game")
	{
		// All game modes except for AI must go through the proper initialization page
		if (localStorage.getItem("gameMode") != "ai" && !localStorage.getItem("match_id"))
		{
			window.location.hash = '#dashboard';
			console.error('Cannot access #game without a match ID');
			showToast("Error", "Cannot start game session", null, "t_openingWsError");
			return;
		}
	}
	else if (window.location.hash === "#lobby-tnmt" && !localStorage.getItem("tournament_id"))
	{
		window.location.hash = '#dashboard';
		console.error('Cannot access #lobby-tnmt without a tournament ID');
		showToast("Error", "Cannot start game session", null, "t_openingWsError");
		return;
	}

	const route = window.location.hash || '';
	const path = routes[route] || routes['404'];

	await loadContent(path);
};

// Status websocket should only (re)open on load event, not on hash change
const handleLoadEvent = async () => {
	await router();
	if (localStorage.getItem("access")) {
		// console.log("Access in event listened for status ws: ", localStorage.getItem("access"));
		openStatusWebsocket();
	}
};

window.addEventListener('hashchange', router);
window.addEventListener('load', handleLoadEvent);

// Redirection when the page logo in top left is clicked
export function redirectToHome(event) {
	event.preventDefault();
	
	// If user is logged in, go to dashboard, otherwise to login page
	if (appState.loggedIn) {
		// If a player is inside a lobby, they can only be redirected via the Cancel button
		if (window.location.hash == '#lobby-game' || window.location.hash == '#lobby-tnmt')
			return;
		// If a player is inside a live game, they will be asked to confirm first
		// UPDATE: Leaving the game via the app is now forbidden
		if (window.location.hash == '#game')
		{
			// const userConfirmed = confirm("Do you really want to leave an ongoing game?");
			// if (!userConfirmed)
			// 	return;
			// else
			// {
			// 	closeLocalWebsocket();
			// 	closeMatchmakingWebsocket();
			// 	closeRematchWebsocket();
			// 	closeTournamentWebsocket();
			// 	closeLocalTournamentWebsocket()
			// 	closePongWebsocket();
			// 	closeAIPlayWebsocket();
			// 	localStorage.removeItem('match_id');
			// 	localStorage.removeItem('tournament_id');
			// }
			return;
		}
		window.location.hash = '#dashboard';
	} else {
		window.location.hash = '#login';
	}
}

// Attach the redirect function to the window object so the rerouting is global
window.redirectToHome = redirectToHome;

// Logout procedure

export async function logout() {
	try {
		appState.isLoggingOut = true;

		const response = await apiCallAuthed("/api/auth/login/refresh/logout", "POST");
		const broadcastChannel = new BroadcastChannel("ws_channel");
		broadcastChannel.postMessage("logout");

		localStorage.removeItem('access');
		localStorage.removeItem('access_expiration');
		sessionStorage.removeItem('uuid');
		localStorage.removeItem('id');
		localStorage.removeItem('match_id');
		Cookies.remove('csrftoken');

		appState.loggedIn = false;
		window.location.hash = '#login';

		// console.log('Logged out successfully');
	} catch (error) {
		console.error('Error during logout:', error);
		showToast("Error during logout", null, error, "t_logoutDuringGame");
	} finally {
		appState.isLoggingOut = false;
	}
}

window.logout = logout;

// On tab close, delete match_id & tournament_id (to keep track of app state)
window.addEventListener('beforeunload', (event) => {
	localStorage.removeItem('match_id');

	// if (window.location.hash == '#lobby-tnmt')
	// 	apiCallAuthed(`/api/tournament/join/cancel/${localStorage.getItem("tournament_id")}/`, "POST");

	localStorage.removeItem('tournament_id');

});