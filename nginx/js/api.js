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
		const response = await fetch(url, options);
		if (response.ok) {
			return await response.json();
		} else {
			const errorData = await response.json();
			throw new Error(errorData.message || 'Registration failed');
		}
	} catch (error) {
		console.error('API call error:', error);
		throw error;
	}
}

export async function loginUser(payload) {
	const url = '/api/auth/token';
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
			return await response.json();
		} else {
			const errorData = await response.json();
			throw new Error(errorData.message || 'Login failed');
		}
	} catch (error) {
		console.error('API call error:', error);
		throw error;
	}
}

export async function apiCallAuthed(url, method = 'GET', headers = {}, payload = null) {
	const options = {
		method,
		headers: {
			...headers,
			'Authorization': `Bearer ${sessionStorage.getItem('access')}`
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
		let response = await fetch(url, options);
		if (response.ok) {
			return await response.json();
		} else if (response.status === 401) {
			// If access token is expired, try to refresh it
			const refreshResponse = await fetch('/api/auth/token/refresh', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ refresh: sessionStorage.getItem('refresh') })
			});

			if (refreshResponse.ok) {
				const refreshData = await refreshResponse.json();
				sessionStorage.setItem('access', refreshData.access);

				// Retry the original request with the new access token
				options.headers['Authorization'] = `Bearer ${refreshData.access}`;
				response = await fetch(url, options);

				if (response.ok) {
					return await response.json();
				} else {
					const errorData = await response.json();
					throw new Error(errorData.message || 'API call status not OK after token refresh');
				}
			} else {
				const errorData = await refreshResponse.json();
				throw new Error(errorData.message || 'Token refresh failed');
			}
		} else {
			const errorData = await response.json();
			throw new Error(errorData.message || 'API call status not OK');
		}
	} catch (error) {
		console.error('API call error:', error);
		throw error;
	}
}