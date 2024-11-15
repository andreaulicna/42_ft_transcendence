import { registerUser } from './api.js';

export function init() {
	const form = document.getElementById('registrationForm');
	if (form) {
		form.addEventListener('submit', async function(event) {
			event.preventDefault();
			const username = document.getElementById('inputUsername').value;
			const email = document.getElementById('inputEmail').value;
			const password = document.getElementById('inputPassword').value;

			const payload = {
				username: username,
				password: password,
				email	: email
			};

			try {
				const data = await registerUser(payload);
				console.log('Registration successful:', data);
				// Redirect to dashboard upon succesful registration
				window.location.hash = '#login';
			} catch (error) {
				console.error('Registration failed:', error);
			}
		});
	}
}