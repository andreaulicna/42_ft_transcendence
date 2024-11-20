import { loginUser } from './api.js';
import { openFriendlistWebsocket } from './websockets.js';

export function init() {
	const form = document.getElementById('loginForm');
	if (form) {
		form.addEventListener('submit', async function(event) {
			event.preventDefault();
			const username = document.getElementById('inputUsername').value;
			const password = document.getElementById('inputPassword').value;

			const payload = {
				username: username,
				password: password
			};

			try {
				const data = await loginUser(payload);
				console.log('Login successful:', data);
				// Store tokens in session storage
				sessionStorage.setItem('access', data.access);
				// Establish friendlist websocket
				openFriendlistWebsocket();
				// Redirect to dashboard upon succesful authentization
				window.location.hash = '#dashboard';
			} catch (error) {
				console.error('Login failed:', error);
			}
		});
	}
}
