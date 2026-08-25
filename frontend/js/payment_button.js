async function startPayment(reservationId) {
  try {
    const response = await fetch("http://127.0.0.1:8000/payments/start", {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify({
        reservation_id: Number(reservationId),
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      alert(
        typeof data.detail === "string"
          ? data.detail
          : "امکان شروع پرداخت وجود ندارد.",
      );

      return null;
    }

    console.log("Payment response:", data);

    return data;
  } catch (error) {
    console.error("Payment error:", error);

    alert("خطا در ارتباط با سرور.");

    return null;
  }
}

const paymentButton = document.getElementById("final-payment-btn");

if (paymentButton) {
  paymentButton.addEventListener("click", async () => {
    const reservationId = localStorage.getItem("reservationId");

    if (!reservationId) {
      alert("رزرو پیدا نشد.");
      return;
    }

    const payment = await startPayment(reservationId);

    if (!payment) {
      return;
    }

    console.log("Amount:", payment.amount);

    // When real gateway is connected:
    //
    // window.location.href =
    //   payment.payment_url;
  });
}
