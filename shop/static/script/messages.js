document.addEventListener("DOMContentLoaded", function () {
    const messages = document.querySelectorAll('.message');
    messages.forEach(function (msg) {
        setTimeout(() => {
            msg.classList.add('hidden');
            //Remove from dom after effect
            setTimeout(() => {
                msg.remove();
            }, 500);
        }, 4000);
    });
});
