import { showLoading } from "./animations.js";
import { hideLoading } from "./animations.js";

export async function registerUser(payload) {
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
			throw new Error(errorData.message || 'Registration failed');
		}
	} catch (error) {
		console.error('Registration API call error:', error);
		throw error;
	} finally {
		hideLoading();
	}
}

export async function loginUser(payload) {
	const url = '/api/auth/login';
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
			throw new Error(errorData.message || 'Login failed');
		}
	} catch (error) {
		console.error('Login API call error:', error);
		throw error;
	} finally {
		hideLoading();
	}
}

export async function apiCallAuthed(url, method = 'GET', headers = {}, payload = null, showAnimation = true) {
	const accessTokenExpiration = parseInt(sessionStorage.getItem('access_expiration'), 10);
	const now = Date.now();

	// Check if the access token is about to expire
	if (now >= accessTokenExpiration - 3000) { // Refresh the token 3 seconds before it expires
		await refreshAccessToken();
	}

	const options = {
		method,
		headers: {
			...headers,
			'Authorization': `Bearer ${sessionStorage.getItem('access')}`,
			'X-CSRFToken': Cookies.get("csrftoken")
		}
	};

	if (payload) {
		if (payload instanceof FormData) {
			options.body = payload;
			delete options.headers['Content-Type'];
		} else {
			options.headers['Content-Type'] = 'application/json';
			options.body = JSON.stringify(payload);
		}
	}

	try {
		if (showAnimation == true)
			showLoading();
		const response = await fetch(url, options);
		const data = await response.json()
		if (response.ok) {
			console.log("API CALL RESPONSE", data);
			return (data);
		} else {
			throw new Error(data.message || 'API call status not OK');
		}
	} catch (error) {
		console.error('Authenticated API call error:', error);
		throw error;
	} finally {
		if (showAnimation == true)
			hideLoading();
	}
}

async function refreshAccessToken() {
	const url = '/api/auth/login/refresh';
	const options = {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			'X-CSRFToken': Cookies.get("csrftoken")
		},
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
		} else {
			const errorData = await response.json();
			throw new Error(errorData.message || 'Token refresh failed');
		}
	} catch (error) {
		console.error('Token refresh error:', error);
		throw error;
	}
}