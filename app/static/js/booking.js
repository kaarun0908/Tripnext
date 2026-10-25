// Booking calculator and inventory live validation
document.addEventListener('DOMContentLoaded', function () {
    // 1. Hotel Room Booking Calculator
    const checkInInput = document.getElementById('hotel-checkin');
    const checkOutInput = document.getElementById('hotel-checkout');
    const guestsInput = document.getElementById('hotel-guests');
    const priceDisplay = document.getElementById('calculated-total-display');
    const nightsDisplay = document.getElementById('nights-count-display');
    const availMessage = document.getElementById('availability-feedback');
    const roomBookingBtn = document.getElementById('room-submit-btn');

    const pricePerNight = parseFloat(document.getElementById('room-price-per-night')?.value || '0');
    const roomId = document.getElementById('room-id-field')?.value;

    function recalculateRoomTotal() {
        if (!checkInInput || !checkOutInput || !priceDisplay) return;

        const checkInVal = checkInInput.value;
        const checkOutVal = checkOutInput.value;

        if (checkInVal && checkOutVal) {
            const start = new Date(checkInVal);
            const end = new Date(checkOutVal);
            const diffTime = end - start;
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

            if (diffDays > 0) {
                const total = diffDays * pricePerNight;
                if (nightsDisplay) nightsDisplay.textContent = `${diffDays} night(s)`;
                priceDisplay.textContent = `₹${total.toLocaleString('en-IN', { minimumFractionDigits: 2 })}`;

                // Query availability
                if (roomId) {
                    fetch(`/bookings/check-availability?room_id=${roomId}&check_in=${checkInVal}&check_out=${checkOutVal}`)
                        .then(res => res.json())
                        .then(data => {
                            if (availMessage) {
                                availMessage.innerHTML = `<span class="badge ${data.available ? 'bg-success' : 'bg-danger'}">${data.message}</span>`;
                            }
                            if (roomBookingBtn) {
                                roomBookingBtn.disabled = !data.available;
                            }
                        })
                        .catch(() => {
                            if (availMessage) availMessage.innerHTML = '';
                        });
                }
            } else {
                if (nightsDisplay) nightsDisplay.textContent = 'Invalid dates';
                priceDisplay.textContent = '₹0.00';
                if (availMessage) availMessage.innerHTML = '<span class="badge bg-warning text-dark">Check-out must be after check-in.</span>';
                if (roomBookingBtn) roomBookingBtn.disabled = true;
            }
        }
    }

    if (checkInInput && checkOutInput) {
        checkInInput.addEventListener('change', recalculateRoomTotal);
        checkOutInput.addEventListener('change', recalculateRoomTotal);
        // Initial run
        recalculateRoomTotal();
    }

    // 2. Package Booking Calculator
    const packageGuestsInput = document.getElementById('package-guests-input');
    const packagePricePerPerson = parseFloat(document.getElementById('package-price-per-person')?.value || '0');
    const packageTotalDisplay = document.getElementById('package-total-display');

    if (packageGuestsInput && packageTotalDisplay && packagePricePerPerson) {
        function recalculatePackageTotal() {
            const guests = parseInt(packageGuestsInput.value, 10) || 1;
            const total = guests * packagePricePerPerson;
            packageTotalDisplay.textContent = `₹${total.toLocaleString('en-IN', { minimumFractionDigits: 2 })}`;
        }
        packageGuestsInput.addEventListener('input', recalculatePackageTotal);
        recalculatePackageTotal();
    }
});
