// Overlay loading animation
export function showLoading() {
	const loadingOverlay = document.getElementById('loadingOverlay');
	if (loadingOverlay) {
		loadingOverlay.classList.add('active');
	}
}

export function hideLoading() {
	const loadingOverlay = document.getElementById('loadingOverlay');
	if (loadingOverlay) {
		loadingOverlay.classList.remove('active');
	}
}

// Placeholder HTML replacement with dynamic text
export function textDynamicLoad(htmlElementID, dynamicContent) {
	const placeholder = document.getElementById(htmlElementID);
	placeholder.textContent = dynamicContent;
	placeholder.classList.add('fadeAnimation');
}

// Text dot dot dot loading animation
export function textDotLoading(htmlElementID) {
	const loadingAnimation = document.getElementById(htmlElementID);
	let dots = 0;
	const animationSpeed = 400;

	const intervalId = setInterval(() => {
		dots = (dots + 1) % 4;
		loadingAnimation.textContent = '.'.repeat(dots) || '.';
	}, animationSpeed);

	// Clear the interval when the page unloads
	if (!window.beforeunloadListenerAdded) {
		window.addEventListener('beforeunload', () => {
			clearInterval(intervalId);
		});
	}

}