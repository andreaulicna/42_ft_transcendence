import { showLoading } from "./animations.js";
import { hideLoading } from "./animations.js";
import { listenStatusRefreshEvent } from "./websockets.js";

export async function apiCallAuthed(url, method = 'GET', headers = {}, payload = null, showAnimation = true) {
	const accessTokenExpiration = parseInt(localStorage.getItem('access_expiration'), 10);
	const now = Date.now();

	// Check if the access token is about to expire
	if (now >= accessTokenExpiration - 3000) { // Refresh the token 3 seconds before it expires
		await refreshAccessToken();
	}

	const options = {
		method,
		headers: {
			...headers,
			'Authorization': `Bearer ${localStorage.getItem('access')}`,
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
			throw new Error(data.message || data.detail || 'API call status not OK');
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
			listenStatusRefreshEvent();
			const refreshStatusSocketEvent = new CustomEvent('refresh_status');
			window.dispatchEvent(refreshStatusSocketEvent);

			const data = await response.json();
			const accessToken = data.access;

			// Decode the JWT to get the expiration time
			const accessTokenPayload = JSON.parse(atob(accessToken.split('.')[1]));
			const accessTokenExpiration = accessTokenPayload.exp * 1000; // Convert to milliseconds

			localStorage.setItem('access', accessToken);
			localStorage.setItem('access_expiration', accessTokenExpiration);
		} else {
			const errorData = await response.json();
			throw new Error(errorData.message || 'Token refresh failed');
		}
	} catch (error) {
		console.error('Token refresh error:', error);
		throw error;
	}
}