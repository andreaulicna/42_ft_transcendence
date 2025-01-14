export function showToast(header, message)
{
	let toastElement = document.getElementById('dynamicToast');
	if (!toastElement) {
		const toastContainer = document.createElement('div');
		toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
		toastContainer.innerHTML = `
			<div id="dynamicToast" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
				<div class="toast-header">
					<strong class="me-auto" id="dynamicToastHeader">Notification</strong>
					<button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
				</div>
				<div class="toast-body" id="dynamicToastMsg">
					This is a dynamic toast message.
				</div>
			</div>
		`;
		document.body.appendChild(toastContainer);
		toastElement = document.getElementById('dynamicToast');
	}

	const toastHeader = document.getElementById('dynamicToastHeader');
	const toastMsg = document.getElementById('dynamicToastMsg');
	const toast = new bootstrap.Toast(toastElement);

	toastHeader.textContent = header;
	toastMsg.textContent = message;

	toast.show();
}