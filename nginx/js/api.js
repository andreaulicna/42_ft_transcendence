import { showLoading } from "./animations.js";
import { hideLoading } from "./animations.js";
import { listenStatusRefreshEvent, closeStatusWebsocket } from "./websockets.js";

export async function apiCallAuthed(url, method = 'GET', headers = {}, payload = null, showAnimation = true) {
	await ensureValidAccessToken();

	const options = {
		method,
		headers: {
			...headers,
			'Authorization': `Bearer ${localStorage.getItem('access')}`,
			'X-CSRFToken': Cookies.get("csrftoken"),
			'Accept-Language' : localStorage.getItem('language') || 'en'
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
			throw new Error(data.message || data.detail || data.details || 'API call status not OK');
		}
	} catch (error) {
		// console.error('Authenticated API call error:', error);
		throw error;
	} finally {
		if (showAnimation == true)
			hideLoading();
	}
}

export async function ensureValidAccessToken() {
	const accessTokenExpiration = parseInt(localStorage.getItem('access_expiration'), 10);
	const now = Date.now();

	// Check if the access token is about to expire
	if (accessTokenExpiration && (now >= accessTokenExpiration - 3000)) { // Refresh the token 3 seconds before it expires
		// console.log("REQUESTING NEW ACCESS TOKEN");
		return await refreshAccessToken();
	}
	return true;
}

function frontendLogout() {
	localStorage.removeItem('access');
	localStorage.removeItem('access_expiration');
	sessionStorage.removeItem('uuid');
	localStorage.removeItem('id');
	localStorage.removeItem('match_id');

	closeStatusWebsocket();
	// window.location.hash = '#login';
}

export async function refreshAccessToken() {
	const csrfToken = Cookies.get("csrftoken");
	if (!csrfToken)
	{
		frontendLogout();
		return false;
	}
	
	const url = '/api/auth/login/refresh';
	const options = {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			'X-CSRFToken': csrfToken,
			'Accept-Language' : localStorage.getItem('language') || 'en'
		},
	};

	try {
		const response = await fetch(url, options);
		// console.log("FETCHING NEW ACCESS TOKEN");
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
			return true;
		} else if (response.status == 401 || response.status == 403) {
			// Handle unauthorized or forbidden response without printing an error
			frontendLogout();
			// IMPORTANT: For the case of 2FA login via Intra (otherwise creates a loop)
			if (window.location.hash == "#2fa" && appState.loginPayloadFor2FA)
				return false;
			window.location.hash = "#login";
			return false;
		} else {
			// Handle other non-OK responses
			const errorData = await response.json();
			throw new Error(errorData.message || 'Token refresh failed');
		}
	} catch (error) {
		// console.error('Token refresh error:', error);

		frontendLogout();
		window.location.hash = "#login";
		return false;
	}
}