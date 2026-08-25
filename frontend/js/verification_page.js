const verificationForm = document.getElementById("verification-form");
const codeInput = document.getElementById("verification-code");
const verifyButton = document.getElementById("verify-btn");
const resendButton = document.getElementById("resend-code-btn");
const messageElement = document.getElementById("verification-message");

const countdownElement = document.getElementById("countdown");
const resendText = document.getElementById("resend-text");

const reservationId = localStorage.getItem("reservationId");

const COUNTDOWN_SECONDS = 120;

let countdownTimer = null;

// ==========================
// MESSAGE
// ==========================

function showMessage(message, type = "error") {
  messageElement.textContent = message;

  messageElement.className = `verification-message ${type}`;

  messageElement.hidden = false;
}

function clearMessage() {
  messageElement.textContent = "";
  messageElement.hidden = true;
}

// ==========================
// COUNTDOWN
// ==========================

function updateCountdown(seconds) {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;

  countdownElement.textContent =
    `${String(minutes).padStart(2, "0")}:` +
    `${String(remainingSeconds).padStart(2, "0")}`;
}

function startCountdown() {
  if (!reservationId) {
    return;
  }

  if (countdownTimer) {
    clearInterval(countdownTimer);
  }

  let seconds = COUNTDOWN_SECONDS;

  resendButton.disabled = true;

  resendButton.textContent = "ارسال مجدد کد";

  resendText.textContent = "ارسال مجدد کد تا";

  countdownElement.hidden = false;

  updateCountdown(seconds);

  countdownTimer = setInterval(() => {
    seconds--;

    updateCountdown(seconds);

    if (seconds <= 0) {
      clearInterval(countdownTimer);

      countdownTimer = null;

      countdownElement.hidden = true;

      resendText.textContent = "کد را دریافت نکردید؟";

      resendButton.disabled = false;

      resendButton.textContent = "ارسال مجدد کد";
    }
  }, 1000);
}

// ==========================
// CHECK RESERVATION
// ==========================

if (!reservationId) {
  showMessage("اطلاعات رزرو پیدا نشد. لطفاً دوباره رزرو را انجام دهید.");

  verifyButton.disabled = true;

  resendButton.disabled = true;

  if (countdownElement) {
    countdownElement.hidden = true;
  }
} else {
  startCountdown();
}

// ==========================
// ONLY ALLOW NUMBERS
// ==========================

codeInput.addEventListener("input", () => {
  codeInput.value = codeInput.value.replace(/\D/g, "").slice(0, 6);

  clearMessage();
});

// ==========================
// VERIFY CODE
// ==========================

verificationForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  if (!reservationId) {
    return;
  }

  const code = codeInput.value.trim();

  if (code.length !== 6) {
    showMessage("لطفاً کد ۶ رقمی را کامل وارد کنید.");

    return;
  }

  verifyButton.disabled = true;

  verifyButton.textContent = "در حال بررسی...";

  clearMessage();

  try {
    const result = await verifyCode(reservationId, code);

    if (!result.success) {
      showMessage(result.detail || "کد تایید صحیح نیست.");

      verifyButton.disabled = false;

      verifyButton.textContent = "تایید شماره تلفن";

      return;
    }

    showMessage("شماره تلفن با موفقیت تایید شد.", "success");

    if (countdownTimer) {
      clearInterval(countdownTimer);
    }

    setTimeout(() => {
      window.location.href = "payment.html";
    }, 700);
  } catch (error) {
    console.error("Verification error:", error);

    showMessage("خطایی رخ داد. لطفاً دوباره تلاش کنید.");

    verifyButton.disabled = false;

    verifyButton.textContent = "تایید شماره تلفن";
  }
});

// ==========================
// RESEND CODE
// ==========================

resendButton.addEventListener("click", async () => {
  if (!reservationId || resendButton.disabled) {
    return;
  }

  resendButton.disabled = true;

  resendButton.textContent = "در حال ارسال...";

  clearMessage();

  try {
    const sent = await sendVerificationCode(reservationId);

    if (!sent) {
      showMessage("ارسال مجدد کد با خطا مواجه شد.");

      resendButton.disabled = false;

      resendButton.textContent = "ارسال مجدد کد";

      return;
    }

    showMessage("کد جدید ارسال شد.", "success");

    codeInput.value = "";

    codeInput.focus();

    startCountdown();
  } catch (error) {
    console.error("Resend verification error:", error);

    showMessage("ارسال مجدد کد با خطا مواجه شد.");

    resendButton.disabled = false;

    resendButton.textContent = "ارسال مجدد کد";
  }
});
