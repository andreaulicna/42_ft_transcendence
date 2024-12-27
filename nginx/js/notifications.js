// This function requires the toast HTML to be loaded on the page
export function showToast(header, message) {
	const toastHeader = document.getElementById('dynamicToastHeader');
	const toastMsg = document.getElementById('dynamicToastMsg');
	const toastElement = document.getElementById('dynamicToast');
	const toast = new bootstrap.Toast(toastElement);

	toastHeader.textContent = header;
	toastMsg.textContent = message;

	toast.show();
}