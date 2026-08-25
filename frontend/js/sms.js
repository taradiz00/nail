async function sendVerificationCode(reservationId) {
  try {
    console.log("SENDING VERIFICATION FOR RESERVATION:", reservationId);
    const response = await fetch(
      `http://127.0.0.1:8000/verification/send/${reservationId}`,
      {
        method: "POST",
      },
    );

    const data = await response.json();
    console.log("SEND VERIFICATION RESPONSE:", response.status, data);

    if (!response.ok) {
      alert(
        typeof data.detail === "string" ? data.detail : "خطا در ارسال کد تایید",
      );

      return false;
    }

    return true;
  } catch (error) {
    console.error("SMS send error:", error);

    alert("خطا در ارتباط با سرور.");

    return false;
  }
}

async function verifyCode(reservationId, code) {
  try {
    const response = await fetch("http://127.0.0.1:8000/verification/confirm", {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify({
        reservation_id: Number(reservationId),
        code: code,
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      return {
        success: false,
        detail:
          typeof data.detail === "string" ? data.detail : "کد تایید صحیح نیست.",
      };
    }

    return {
      success: data.verified === true,
      detail: "",
    };
  } catch (error) {
    console.error("Verification error:", error);

    return {
      success: false,
      detail: "خطا در ارتباط با سرور.",
    };
  }
}
