import { apiCallAuthed } from './api.js';

const dynamicContent = document.getElementById('dynamicContent');

const routes = {
	''				: '/pages/login.html',
	'#login'		: '/pages/login.html',
	'#register'		: '/pages/register.html',
	'#dashboard'	: '/pages/dashboard.html',
	'#game'			: '/pages/game.html',
	'#tournament'	: '/pages/tournament.html',
	'#profile'		: '/pages/profile.html',
	'404'			: '/pages/404.html'
};

const loadContent = async (path) => {
	try {
		const response = await fetch(path);
		const content = await response.text();
		dynamicContent.innerHTML = content;
		let data;

		// Reapply language settings after loading new content
		const preferredLanguage = localStorage.getItem("language") || "en";
		setLanguage(preferredLanguage);

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
		} else if (window.location.hash === '#game') {
			import('/js/gameRemote.js').then(module => module.init());
		} else if (window.location.hash === '#tournament') {
			import('/js/tournament.js').then(module => module.init());
		}
	} catch (err) {
		console.error('Error loading content:', err);
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
export function logout(event) {
	event.preventDefault();
	
	const accessToken = sessionStorage.getItem('access');
	if (accessToken) {
		sessionStorage.removeItem('access');
		sessionStorage.removeItem('access_expiration');
		sessionStorage.removeItem('uuid');
		Cookies.remove('csrftoken');
		window.location.hash = '#login';
	}
}

window.logout = logout;