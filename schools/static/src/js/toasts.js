document.addEventListener('DOMContentLoaded', () => {
    function showToast() {
        const toast = document.getElementById('toast-success');
        toast.classList.remove('hidden');

        // Automatically hide the toast after 3 seconds
        setTimeout(() => {
            toast.classList.add('hidden');
        }, 3000);
    }

    document.addEventListener('show-toast', function () {
        showToast();
    });
});