export async function apiCall(url, method = 'GET', headers = {}, payload = null) {
	const options = {
		method,
		headers: {
			...headers
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
		const response = await fetch(url, options);
		if (response.ok) {
			return await response.json();
		} else {
			const errorData = await response.json();
			throw new Error(errorData.message || 'API call status not OK');
		}
	} catch (error) {
		console.error('API call error:', error);
		throw error;
	}
}