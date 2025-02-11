import { openStatusWebsocket } from './websockets.js';
import { showToast } from "./notifications.js";

async function handle2FASubmit(event) {
	const loginPayload = appState.loginPayloadFor2FA;
	const { username, password } = loginPayload;

	event.preventDefault();
	const code = document.getElementById('2faCode').value;

	const payload = {
		username: username,
		password: password,
		otp_code: code,
	}

	try {
		const data = await login2FA(payload);
		// console.log('Login successful:', data);
		// Store tokens in session storage
		localStorage.setItem('access', data.access);
		// Establish friendlist websocket
		openStatusWebsocket();
		// Redirect to dashboard upon successful authentication
		const newUrl = window.location.origin + window.location.pathname;
		window.history.replaceState({}, document.title, newUrl);
		appState.loggedIn = true;
		window.location.hash = '#dashboard';
	} catch (error) {
		// console.error('Login failed:', error);
		showToast("Login failed", null, error, "t_loginFailed");
	}
}

export function init() {
	if (!appState.loginPayloadFor2FA)
		window.location.hash = "#login";
	const form = document.getElementById('2faForm');
	form.addEventListener('submit', handle2FASubmit);	
}

async function login2FA(payload) {
	// console.log("PAYLOAD:", JSON.stringify(payload))
	const url = '/api/auth/login';
		const options = {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'Accept-Language' : localStorage.getItem('language') || 'en'
			},
			body: JSON.stringify(payload)
		};

		try {
			const response = await fetch(url, options);
			console.log(response);
			if (response.ok) {
				const data = await response.json();

				const accessToken = data.access;

				// Decode the JWT to get the expiration time
				const accessTokenPayload = JSON.parse(atob(accessToken.split('.')[1]));
				const accessTokenExpiration = accessTokenPayload.exp * 1000; // Convert to milliseconds

				localStorage.setItem('access', accessToken);
				localStorage.setItem('access_expiration', accessTokenExpiration);

				return data;
			} else {
				const errorData = await response.json();
				throw new Error(errorData.detail);
			}
		} catch (error) {
			// console.error('Login API call error:', error);
			throw error;
		}
}