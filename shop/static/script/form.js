document.addEventListener('DOMContentLoaded', function () {
    const purchased = document.getElementById('id_is_purchased');
    const leased = document.getElementById('id_is_leased');

    const purchasePrice = document.getElementById('id_purchase_price');
    const leasingPrice = document.getElementById('id_leasing_price');

    if (!purchased || !leased) return;

    const formMessages = document.querySelectorAll('ul.errorlist');

    formMessages.forEach(formMessages => {
        formMessages.classList.add('hidden-message');
    });

    function updateState() {
        // --- checkboxpart ---
        if (purchased.checked) {
            leased.checked = false;
            leased.disabled = true;
        } else {
            leased.disabled = false;
        }

        if (leased.checked) {
            purchased.checked = false;
            purchased.disabled = true;
        } else {
            purchased.disabled = false;
        }

        // --- price part ---
        if (purchased.checked && !leased.checked) {
            // purchase only
            purchasePrice.disabled = false;
            leasingPrice.disabled = true;
            leasingPrice.value = '';
        } else if (leased.checked && !purchased.checked) {
            // leased only
            leasingPrice.disabled = false;
            purchasePrice.disabled = true;
            purchasePrice.value = '';
        } else if (!purchased.checked && !leased.checked) {
            purchasePrice.disabled = true;
            leasingPrice.disabled = true;
        } else {
            purchasePrice.disabled = false;
            leasingPrice.disabled = false;
        }
    }

    purchased.addEventListener('change', updateState);
    leased.addEventListener('change', updateState);

    updateState();
});
