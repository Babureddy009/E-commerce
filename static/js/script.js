document.addEventListener("DOMContentLoaded", () => {

    document.querySelectorAll(".product-card").forEach(card => {

        const pid = card.dataset.productId;
        const qtyArea = card.querySelector(".qty-area");
        const addBtn = card.querySelector(".add-btn");

        // ---------------- ADD TO CART ----------------
        if (addBtn) {
            addBtn.addEventListener("click", () => {

                // 🔒 prevent double click
                addBtn.disabled = true;

                fetch("/api/cart/add", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ product_id: pid })
                })
                .then(res => res.json())
                .then(() => {
                    // 🔥 ALWAYS start from quantity 1
                    qtyArea.innerHTML = quantityControls(1);
                    attachQtyEvents(qtyArea, pid);
                })
                .catch(() => {
                    addBtn.disabled = false;
                });

            });
        }
    });
});


// ---------------- QTY CONTROLS HTML ----------------
function quantityControls(qty) {
    return `
        <button class="qty-btn minus">-</button>
        <span class="qty">${qty}</span>
        <button class="qty-btn plus">+</button>
    `;
}


// ---------------- ATTACH + / - EVENTS ----------------
function attachQtyEvents(container, pid) {

    const plusBtn = container.querySelector(".plus");
    const minusBtn = container.querySelector(".minus");

    plusBtn.addEventListener("click", () => {
        updateQty(pid, "plus", container);
    });

    minusBtn.addEventListener("click", () => {
        updateQty(pid, "minus", container);
    });
}


// ---------------- UPDATE QTY API ----------------
function updateQty(pid, action, container) {

    fetch("/api/cart/update", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ product_id: pid, action: action })
    })
    .then(res => res.json())
    .then(data => {

        if (data.quantity <= 0) {
            // back to Add to Cart
            container.innerHTML = `<button class="add-btn">Add to Cart</button>`;

            // reattach add button event
            container.querySelector(".add-btn").addEventListener("click", () => {
                fetch("/api/cart/add", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ product_id: pid })
                })
                .then(() => {
                    container.innerHTML = quantityControls(1);
                    attachQtyEvents(container, pid);
                });
            });

        } else {
            container.innerHTML = quantityControls(data.quantity);
            attachQtyEvents(container, pid);
        }
    });
}
