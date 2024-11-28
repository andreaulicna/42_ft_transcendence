import { textDotLoading } from './animations.js';

export function init() {
	const returnButton = document.getElementById('cancelBtn');
	if (returnButton) {
		returnButton.addEventListener('click', () => {
			window.location.hash = '#dashboard';
		});
	}

	textDotLoading("loadingAnimation");
}