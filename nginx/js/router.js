import { apiCallAuthed } from './api.js';
import { showLoading } from "./animations.js";
import { hideLoading } from "./animations.js";

const dynamicContent = document.getElementById('dynamicContent');

const routes = {
	''				: '/pages/login.html',
	'#login'		: '/pages/login.html',
	'#register'		: '/pages/register.html',
	'#dashboard'	: '/pages/dashboard.html',
	'#searching'	: '/pages/searchingForGame.html',
	'#game'			: '/pages/game.html',
	'#tournament'	: '/pages/tournament.html',
	'#lobby'		: '/pages/tournamentLobby.html',
	'#profile'		: '/pages/profile.html',
	'404'			: '/pages/404.html'
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
		if ((path != '/pages/login.html' && path != '/pages/register.html' && path != '/pages/404.html') && !sessionStorage.getItem('access')) {
			window.location.hash = '#login';
			throw new Error('Not logged in.');
		}

		// Import the page's relevant script
		let data;
		if (window.location.hash === '#login' || window.location.hash === '') {
			import('/js/login.js').then(module => module.init());
		} else if (window.location.hash === '#register') {
			import('/js/register.js').then(module => module.init());
		} else if (window.location.hash === '#dashboard') {
			data = await apiCallAuthed('/api/user/info');
			import('/js/dashboard.js').then(module => module.init(data));
		} else if (window.location.hash === '#profile') {
			data = await apiCallAuthed('/api/user/info');
			import('/js/profile.js').then(module => module.init(data));
		} else if (window.location.hash === '#searching') {
			import('/js/gameSearching.js').then(module => module.init());
		} else if (window.location.hash === '#game') {
			data = await apiCallAuthed(`/api/user/match/${sessionStorage.getItem("match_id")}`);
			import('/js/gameRemote.js').then(module => module.init(data));
		} else if (window.location.hash === '#tournament') {
			import('/js/tournament.js').then(module => module.init());
		} else if (window.location.hash === '#lobby') {
			import('/js/tournamentLobby.js').then(module => module.init());
		}
	} catch (err) {
		console.error('Error loading content:', err);
	} finally {
		hideLoading();
	}
};

const router = () => {
	const route = window.location.hash || '';
	const path = routes[route] || routes['404'];
	// console.log(`Routing to: ${route}, Path: ${path}`);
	loadContent(path);
};

window.addEventListener('hashchange', router);

window.addEventListener('load', router);

// Redirection when the page logo in top left is clicked
export function redirectToHome(event) {
	event.preventDefault();
	
	const accessToken = sessionStorage.getItem('access');
	if (accessToken) {
		// User is logged in, redirect to dashboard
		// console.log('Redirecting as a logged in user');
		window.location.hash = '#dashboard';
	} else {
		// User is not logged in, redirect to login page
		// console.log('Redirecting as a NON-logged in user');
		window.location.hash = '#login';
	}
}

// Attach the redirect function to the window object so the rerouting is global
window.redirectToHome = redirectToHome;

// Logout procedure
export async function logout() {
	try {
		const response = await apiCallAuthed("/api/auth/login/refresh/logout", "POST");
		sessionStorage.removeItem('access');
		sessionStorage.removeItem('access_expiration');
		sessionStorage.removeItem('uuid');
		// Cookies.remove('csrftoken');
		// Cookies.remove('refresh_token', { path: '/', domain: 'yourdomain.com' });
		console.log('Logged out successfully');
	} catch (error) {
		console.error('Error during logout:', error);
	}
}

window.logout = logout;