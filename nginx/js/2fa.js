import { apiCallAuthed } from './api.js';

export function init() {
	const form = document.getElementById('2faForm');
	if (form) {
		form.addEventListener('submit', async function(event) {
			event.preventDefault();
			const code = document.getElementById('2faCode').value;

			try {
				const response = await apiCallAuthed('/api/auth/2fa/verify', 'POST', {}, { code });
				if (response.success) {
					// 2FA verification successful, redirect to dashboard
					window.location.hash = '#dashboard';
				} else {
					alert('Invalid 2FA code. Please try again.');
				}
			} catch (error) {
				console.error('2FA verification failed:', error);
				alert('An error occurred during 2FA verification. Please try again.');
			}
		});
	}
}
