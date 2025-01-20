import { showLoading } from "./animations.js";
import { apiCallAuthed, ensureValidAccessToken } from './api.js';
import { hideLoading } from "./animations.js";
import { openStatusWebsocket, closeStatusWebsocket } from './websockets.js';

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
	'#remote-tnmt'	: '/pages/tournamentRemote.html',
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

		// Reapply language settings after loading new content
		const preferredLanguage = localStorage.getItem("language") || "en";
		setLanguage(preferredLanguage);

		// Check if user is logged in first
		if ((path != '/pages/login.html' && path != '/pages/2fa.html' && path != '/pages/register.html' && path != '/pages/404.html') && !localStorage.getItem('access')) {
			window.location.hash = '#login';
			throw new Error('Not logged in.');
		}
		
		// Refreshes access token before getting to further API calls, preventing double refresh on load/hashchange events
		await ensureValidAccessToken();

		// If user is logged in, go from #login straight to #dashboard
		if (path == '/pages/login.html' && localStorage.getItem('access')) {
			window.location.hash = '#dashboard';
		}

		// Import the page's relevant script
		let data;
		if (window.location.hash === '#login' || window.location.hash === '') {
			await import('/js/login.js').then(module => module.init());
		} else if (window.location.hash === '#register') {
			await import('/js/register.js').then(module => module.init());
		} else if (window.location.hash === '#dashboard') {
			// to prevent duplicate calls to api?user/info on load event
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
			console.log("Mode in router", mode);
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
		} else if (window.location.hash === '#remote-tnmt') {
			await import('/js/tournamentRemote.js').then(module => module.init());
		} else if (window.location.hash === '#local-tnmt') {
			await import('/js/tournamentLocal.js').then(module => module.init());
		} else if (window.location.hash === '#lobby-tnmt') {
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
	const route = window.location.hash || '';
	const path = routes[route] || routes['404'];
	// console.log(`Routing to: ${route}, Path: ${path}`);
	// await ensureValidAccessToken();
	await loadContent(path);
};

// Status websocket should only (re)open on load event, not on hash change
const handleLoadEvent = async () => {
    await router();
	if (localStorage.getItem("access")) {
        console.log("Access in event listened for status ws: ", localStorage.getItem("access"));
        openStatusWebsocket();
    }
};

window.addEventListener('hashchange', router);
window.addEventListener('load', handleLoadEvent);

// Redirection when the page logo in top left is clicked
export function redirectToHome(event) {
	event.preventDefault();
	
	const accessToken = localStorage.getItem('access');
	// If user is logged in, go to dashboard, otherwise to login page
	if (accessToken) {
		// If a player is inside a lobby, they can only be redirected via the Cancel button
		if (window.location.hash == '#lobby-game' || window.location.hash == '#lobby-tnmt')
			return;
		// If a player is inside a live game, they will be asked to confirm first
		if (window.location.hash == '#game' && !confirm("Do you really want to leave an ongoing game?"))
			return;
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
		const broadcastChannel = new BroadcastChannel("ws_channel");
    	broadcastChannel.postMessage("logout");

		const response = await apiCallAuthed("/api/auth/login/refresh/logout", "POST");
		localStorage.removeItem('access');
		localStorage.removeItem('access_expiration');
		sessionStorage.removeItem('uuid');
		localStorage.removeItem('id');
		localStorage.removeItem('match_id');

		window.location.hash = '#login';

		// Cookies.remove('csrftoken');
		// Cookies.remove('refresh_token', { path: '/', domain: 'yourdomain.com' });
		console.log('Logged out successfully');
	} catch (error) {
		console.error('Error during logout:', error);
	}
}

window.logout = logout;