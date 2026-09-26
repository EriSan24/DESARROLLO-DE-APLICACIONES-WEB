document.addEventListener("DOMContentLoaded", () => {
	const lineList = document.querySelector("#invoice-lines");
	if (!lineList) return;

	const lineTemplate = document.querySelector("#invoice-line-template");
	const addButton = document.querySelector("#add-invoice-line");
	const discountField = document.querySelector("#descuento_pct");
	const taxRate = Number(lineList.dataset.taxRate || 0.15);

	const money = (value) => `$${value.toFixed(2)}`;
	const recalculate = () => {
		let subtotal = 0;
		lineList.querySelectorAll(".invoice-line").forEach((line) => {
			const product = line.querySelector(".line-product");
			const quantityField = line.querySelector(".line-quantity");
			const option = product.selectedOptions[0];
			const price = Number(option?.dataset.price || 0);
			const quantity = Math.max(0, Number(quantityField.value || 0));
			const available = Number(option?.dataset.stock || 9999);
			quantityField.max = String(available);
			if (quantity > available) quantityField.setCustomValidity(`Solo hay ${available} unidades disponibles.`);
			else quantityField.setCustomValidity("");
			subtotal += price * quantity;
		});
		const discountRate = Math.min(100, Math.max(0, Number(discountField?.value || 0))) / 100;
		const discount = subtotal * discountRate;
		const tax = (subtotal - discount) * taxRate;
		document.querySelector("#invoice-subtotal").textContent = money(subtotal);
		document.querySelector("#invoice-discount").textContent = money(discount);
		document.querySelector("#invoice-tax").textContent = money(tax);
		document.querySelector("#invoice-total").textContent = money(subtotal - discount + tax);
	};

	addButton?.addEventListener("click", () => {
		lineList.append(lineTemplate.content.cloneNode(true));
		recalculate();
	});

	lineList.addEventListener("input", recalculate);
	lineList.addEventListener("change", recalculate);
	lineList.addEventListener("click", (event) => {
		const removeButton = event.target.closest(".remove-invoice-line");
		if (!removeButton) return;
		const lines = lineList.querySelectorAll(".invoice-line");
		if (lines.length > 1) removeButton.closest(".invoice-line").remove();
		else {
			lines[0].querySelector(".line-product").value = "";
			lines[0].querySelector(".line-quantity").value = "1";
		}
		recalculate();
	});
	discountField?.addEventListener("input", recalculate);
	recalculate();
});