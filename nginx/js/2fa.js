import { openFriendlistWebsocket } from './websockets.js';

export function init() {
	const loginPayload = JSON.parse(sessionStorage.getItem("login_payload"));
	sessionStorage.removeItem("login_payload");
    const { username, password } = loginPayload;

	const form = document.getElementById('2faForm');
	form.addEventListener('submit', async (event) => {
		event.preventDefault();
		const code = document.getElementById('2faCode').value;

		const payload = {
			username: username,
			password: password,
			otp_code: code,
		}

		try {
			const data = await login2FA(payload);
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

async function login2FA(payload) {
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