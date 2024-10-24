import { apiCall } from './api.js';

export function init() {
	const form = document.getElementById('registrationForm');
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
				const data = await apiCall('replace with api call!', 'POST', {}, payload);
				console.log('Registration successful:', data);
			} catch (error) {
				console.error('Registration failed:', error);
			}
		});
	}
}