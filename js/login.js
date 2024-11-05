import { loginUser } from './api.js';

export function init() {
	const form = document.getElementById('loginForm');
	if (form) {
		form.addEventListener('submit', async function(event) {
			event.preventDefault();
			const email = document.getElementById('inputEmail').value;
			const password = document.getElementById('inputPassword').value;

			const payload = {
				username: email,
				password: password
			};

			try {
				const data = await loginUser(payload);
				console.log('Login successful:', data);
				// Store tokens in session storage
				sessionStorage.setItem('access', data.access);
				sessionStorage.setItem('refresh', data.refresh);
			} catch (error) {
				console.error('Login failed:', error);
			}
		});
	}
}