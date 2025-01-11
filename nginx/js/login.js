import { openStatusWebsocket } from './websockets.js';

let form = document.getElementById('loginForm');
let errorToastElement = document.getElementById('errorLoginToast');
let errorToast = new bootstrap.Toast(errorToastElement);
let loginIntraBtn = document.getElementById("loginIntra");

export function init() {
	checkForAccessToken();

	if (form) {
		form.addEventListener('submit', async function(event) {
			event.preventDefault();
			const username = document.getElementById('inputUsernameLogin').value;
			const password = document.getElementById('inputPasswordLogin').value;

			const payload = {
				username: username,
				password: password
			};

			try {
				const data = await loginUser(payload);
				console.log('Login successful:', data);
				// Store tokens in local storage
				localStorage.setItem('access', data.access);
				// Establish friendlist websocket
				openStatusWebsocket();
				// Redirect to dashboard upon succesful authentization
				window.location.hash = '#dashboard';
			} catch (error) {
				console.error('Login failed:', error);
				errorToast.show();
			}
		});
	}

	loginIntraBtn.addEventListener("click", loginIntra);
}

function checkForAccessToken() {
	const urlParams = new URLSearchParams(window.location.search);
	const accessToken = urlParams.get('access_token');
	if (accessToken) {
		const accessTokenPayload = JSON.parse(atob(accessToken.split('.')[1]));
		const accessTokenExpiration = accessTokenPayload.exp * 1000;

		localStorage.setItem('access', accessToken);
		localStorage.setItem('access_expiration', accessTokenExpiration);

		const newUrl = window.location.origin + window.location.pathname;
        window.history.replaceState({}, document.title, newUrl);
		window.location.hash = '#dashboard';
	}
}

async function loginIntra() {
	const url = "/api/auth/intra";
	const options = {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
		},
	};
	
	try {
		const response = await fetch(url, options);
		if (response.ok) {
			const data = await response.json();
			console.log(data);
			window.location.href = data.URL;
		}
		else {
			throw new Error(response.status);
		}
	} catch (error) {
		console.error('Intra login failed:', error);
		errorToast.show();
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
				localStorage.setItem('login_payload', JSON.stringify(payload));
				window.location.hash = '#2fa';
			}

			const accessToken = data.access;

			// Decode the JWT to get the expiration time
			const accessTokenPayload = JSON.parse(atob(accessToken.split('.')[1]));
			const accessTokenExpiration = accessTokenPayload.exp * 1000; // Convert to milliseconds

			localStorage.setItem('access', accessToken);
			localStorage.setItem('access_expiration', accessTokenExpiration);

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