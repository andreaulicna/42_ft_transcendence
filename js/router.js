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

		if (window.location.hash === '#login') {
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
			data = await apiCallAuthed('/api/user/match');
			import('/js/game.js').then(module => module.init(data));
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
	loadContent(path);
};

window.addEventListener('hashchange', router);

window.addEventListener('load', router);
