export function showToast(header, message = null, error = null, langId = null) {
	let toastContainer = document.getElementById('toastContainer');
	if (!toastContainer) {
		toastContainer = document.createElement('div');
		toastContainer.id = 'toastContainer';
		toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
		document.body.appendChild(toastContainer);
	}

	const toastId = `toast-${Date.now()}`;
	const toastElement = document.createElement('div');
	toastElement.id = toastId;
	toastElement.className = 'toast';
	toastElement.role = 'alert';
	toastElement.ariaLive = 'assertive';
	toastElement.ariaAtomic = 'true';

	const headerTranslateAttr = langId ? `data-translate="${langId}_header"` : '';
	const messageTranslateAttr = langId ? `data-translate="${langId}_message"` : '';

	let toastBodyContent = '';
	if (message)
		toastBodyContent += `<span ${messageTranslateAttr}>${message}</span>`;
	if (error)
		toastBodyContent += (toastBodyContent ? '<br><br>' : '') + "Server: " + error;

	toastElement.innerHTML = `
		<div class="toast-header">
			<strong class="me-auto" ${headerTranslateAttr}>${header}</strong>
			<button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
		</div>
		<div class="toast-body">
			${toastBodyContent}
		</div>
	`;

	toastContainer.appendChild(toastElement);

	const toast = new bootstrap.Toast(toastElement);
	toast.show();
}