import { showLoading } from "./animations.js";
import { hideLoading } from "./animations.js";
import { showToast } from "./notifications.js";

export function init() {
	const form = document.getElementById('registrationForm');

	if (form) {
		form.addEventListener('submit', async function(event) {
			event.preventDefault();
			const username = document.getElementById('inputUsernameRegister').value;
			const email = document.getElementById('inputEmailRegister').value;
			const password = document.getElementById('inputPasswordRegister').value;

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
				showToast("Registration failed", null, error, "t_registrationFailed");
			}
		});
	}
}

async function registerUser(payload) {
	const url = '/api/user/register';
	const options = {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(payload)
	};

	try {
		showLoading();
		const response = await fetch(url, options);
		if (response.ok) {
			return await response.json();
		} else {
			const errorData = await response.json();
			let errorMessage = '';

			// Concatenate error messages
			for (const [field, messages] of Object.entries(errorData)) {
				errorMessage += `${field}: ${messages.join(' ')}\n`;
			}

			throw new Error(errorMessage || 'Registration failed');
		}
	} catch (error) {
		console.error('Registration API call error:', error);
		throw error;
	} finally {
		hideLoading();
	}
}