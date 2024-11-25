// import { apiCallAuthed } from './api.js';

export function init() {
	
	const returnButton = document.getElementById('cancelBtn');
	if (returnButton) {
		returnButton.addEventListener('click', () => {
			window.location.hash = '#dashboard';
		});
	}

	// Simple loading animation
	const loadingAnimation = document.getElementById("loadingAnimation");
	let dots = 0;
	const animationSpeed = 400;

	const intervalId = setInterval(() => {
		dots = (dots + 1) % 4;
		loadingAnimation.textContent = '.'.repeat(dots) || '.';
	}, animationSpeed);

	// Clear the interval when the page unloads
	window.addEventListener('beforeunload', () => {
		clearInterval(intervalId);
	});
}