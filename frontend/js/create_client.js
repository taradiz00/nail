const clientForm = document.getElementById("client-form");

const selectedServiceIds =
  JSON.parse(localStorage.getItem("selectedServiceIds")) || [];

const selectedDate = localStorage.getItem("selectedDate");

const selectedTime = localStorage.getItem("selectedTime");

if (clientForm) {
  clientForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const name = document.getElementById("client-name").value;

    const email = document.getElementById("client-email").value;

    const phone = document.getElementById("client-phone").value;

    if (!selectedDate || !selectedTime || selectedServiceIds.length === 0) {
      alert("اطلاعات رزرو کامل نیست.");
      return;
    }

    const startAt = `${selectedDate}T${selectedTime}:00`;

    try {
      const response = await fetch("http://127.0.0.1:8000/reservations/", {
        method: "POST",

        headers: {
          "Content-Type": "application/json",
        },

        body: JSON.stringify({
          name,
          phone,
          email: email || null,
          service_ids: selectedServiceIds,
          start_at: startAt,
        }),
      });

      const data = await response.json();
      console.log("Reservation response:", data);

      console.log("Sent values:", {
        name,
        phone,
        email: email || null,
        service_ids: selectedServiceIds,
        start_at: startAt,
      });

      if (!response.ok) {
        if (response.status === 409) {
          alert("این زمان دیگر در دسترس نیست.");
        } else if (response.status === 422) {
          alert("لطفاً اطلاعات وارد شده را بررسی کنید.");
        } else {
          alert(
            typeof data.detail === "string" ? data.detail : "خطایی رخ داد.",
          );
        }

        return;
      }

      // Save reservation ID
      localStorage.setItem("reservationId", data.id);

      // Send verification code
      const smsSent = await sendVerificationCode(data.id);

      if (!smsSent) {
        alert("ارسال کد تایید با خطا مواجه شد.");
        return;
      }

      // Both existing and new clients go here
      window.location.href = "verification.html";
    } catch (error) {
      console.error(error);

      alert("ارتباط با سرور برقرار نشد.");
    }
  });
}

if (window.lucide) {
  lucide.createIcons();
}
