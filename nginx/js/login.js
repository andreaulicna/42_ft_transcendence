import { openFriendlistWebsocket } from './websockets.js';

export function init() {
	const form = document.getElementById('loginForm');
	const errorToastElement = document.getElementById('errorLoginToast');
	const errorToast = new bootstrap.Toast(errorToastElement);
	
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
				errorToast.show();
			}
		});
	}
}

async function loginUser(payload) {
	const url = '/api/auth/login';
	const options = {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(payload)
	};

	try {
		const response = await fetch(url, options);
		if (response.ok) {
			const data = await response.json();
			console.log(data);
			if (data.otp_required)
			{
				console.log("ENTERING 2FA");
				sessionStorage.setItem('login_payload', JSON.stringify(payload));
				window.location.hash = '#2fa';
			}

			const accessToken = data.access;

			// Decode the JWT to get the expiration time
			const accessTokenPayload = JSON.parse(atob(accessToken.split('.')[1]));
			const accessTokenExpiration = accessTokenPayload.exp * 1000; // Convert to milliseconds

			sessionStorage.setItem('access', accessToken);
			sessionStorage.setItem('access_expiration', accessTokenExpiration);

			return data;
		} else {
			const errorData = await response.json();
			throw new Error(errorData.details);
		}
	} catch (error) {
		console.error('Login API call error:', error);
		throw error;
	}
}