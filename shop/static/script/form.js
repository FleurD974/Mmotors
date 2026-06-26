document.addEventListener('DOMContentLoaded', function () {
    const purchased = document.getElementById('id_is_purchased');
    const leased = document.getElementById('id_is_leased');

    const purchasePrice = document.getElementById('id_purchase_price');
    const leasingPrice = document.getElementById('id_leasing_price');

    const formMessages = document.querySelectorAll('ul.errorlist');

    formMessages.forEach(el => {
        el.classList.add('hidden-message');
    });

    function updateState() {

        // --- checkbox UX only ---
        if (purchased.checked) {
            leased.parentElement.classList.add('inactive');
        } else {
            leased.parentElement.classList.remove('inactive');
        }

        if (leased.checked) {
            purchased.parentElement.classList.add('inactive');
        } else {
            purchased.parentElement.classList.remove('inactive');
        }

        // --- price logic UX ---
        if (purchased.checked && !leased.checked) {
            purchasePrice.parentElement.classList.remove('inactive');
            leasingPrice.parentElement.classList.add('inactive');

        } else if (leased.checked && !purchased.checked) {
            leasingPrice.parentElement.classList.remove('inactive');
            purchasePrice.parentElement.classList.add('inactive');

        } else {
            purchasePrice.parentElement.classList.add('inactive');
            leasingPrice.parentElement.classList.add('inactive');
        }
    }

    purchased.addEventListener('change', updateState);
    leased.addEventListener('change', updateState);

    updateState();
});
