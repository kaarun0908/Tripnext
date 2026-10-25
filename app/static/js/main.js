// Main JavaScript for TripNest
document.addEventListener('DOMContentLoaded', function () {
    // 1. Auto-dismiss flash alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 5000);
    });

    // 2. Favourite Heart Toggle AJAX
    const favButtons = document.querySelectorAll('.fav-toggle-btn');
    favButtons.forEach(btn => {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            const destId = this.getAttribute('data-dest-id');
            const icon = this.querySelector('i');

            fetch(`/favourites/toggle/${destId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    if (data.saved) {
                        this.classList.add('active');
                        if (icon) {
                            icon.classList.remove('bi-heart');
                            icon.classList.add('bi-heart-fill');
                        }
                    } else {
                        this.classList.remove('active');
                        if (icon) {
                            icon.classList.remove('bi-heart-fill');
                            icon.classList.add('bi-heart');
                        }
                    }
                }
            })
            .catch(err => {
                console.error('Error toggling favourite:', err);
            });
        });
    });

    // 3. Prevent duplicate form submissions on critical forms
    const paymentForm = document.querySelector('#payment-form');
    if (paymentForm) {
        paymentForm.addEventListener('submit', function () {
            const submitBtn = this.querySelector('button[type="submit"], input[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span> Processing Secure Payment...';
            }
        });
    }
});
