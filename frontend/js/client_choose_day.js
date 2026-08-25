// ==========================================
// LOAD SELECTED SERVICES FROM PREVIOUS PAGE
// ==========================================

const selectedServiceIds =
  JSON.parse(localStorage.getItem("selectedServiceIds")) || [];

// ==========================================
// STATE
// ==========================================

let calDate = new persianDate();
let selectedDateKey = null;
let selectedDate = null;
let selectedTime = null;

// ==========================================
// DOM REFERENCES
// ==========================================

const daysEl = document.getElementById("cal-days");
const monthLabel = document.getElementById("cal-month-label");

const timeBox = document.getElementById("time-box");
const timeBoxTitle = document.getElementById("time-box-title");
const timeSlotsEl = document.getElementById("time-slots");

const summaryEl = document.getElementById("booking-summary");
const summaryText = document.getElementById("booking-summary-text");

const hiddenDate = document.getElementById("reservation-date");
const hiddenTime = document.getElementById("reservation-time");

const continueBtn = document.getElementById("payment-btn");

// ==========================================
// PERSIAN WEEK ORDER
// ==========================================

const weekOrder = [
  "شنبه",
  "یکشنبه",
  "دوشنبه",
  "سه‌شنبه",
  "چهارشنبه",
  "پنجشنبه",
  "جمعه",
];

// ==========================================
// GET WEEKDAY NAME
// ==========================================

function getWeekdayName(pDateObj) {
  const jsDay = pDateObj.toDate().getDay();

  const map = [
    "یکشنبه",
    "دوشنبه",
    "سه‌شنبه",
    "چهارشنبه",
    "پنجشنبه",
    "جمعه",
    "شنبه",
  ];

  return map[jsDay];
}

// ==========================================
// ASK FASTAPI FOR REAL AVAILABLE TIMES
// ==========================================

async function loadAvailableTimes(date) {
  if (selectedServiceIds.length === 0) {
    throw new Error("هیچ خدمتی انتخاب نشده است.");
  }

  console.log("Date sent:", date);
  console.log("Services sent:", selectedServiceIds);

  const response = await fetch("http://127.0.0.1:8000/availability/", {
    method: "POST",

    headers: {
      "Content-Type": "application/json",
    },

    body: JSON.stringify({
      date: date,
      service_ids: selectedServiceIds,
    }),
  });

  const data = await response.json();

  console.log("Availability response:", data);

  if (!response.ok) {
    throw new Error(
      typeof data.detail === "string"
        ? data.detail
        : "خطا در دریافت زمان‌های خالی",
    );
  }

  return data.available_times;
}

// ==========================================
// RENDER PERSIAN CALENDAR
// ==========================================

function renderCalendar() {
  monthLabel.textContent = calDate.format("MMMM YYYY");
  daysEl.innerHTML = "";

  const firstOfMonth = new persianDate([calDate.year(), calDate.month(), 1]);

  const startOffset = weekOrder.indexOf(getWeekdayName(firstOfMonth));

  const daysInMonth = calDate.daysInMonth();

  const today = new persianDate();

  for (let i = 0; i < startOffset; i++) {
    const empty = document.createElement("div");

    empty.className = "cal-day empty";

    daysEl.appendChild(empty);
  }

  for (let day = 1; day <= daysInMonth; day++) {
    const thisDate = new persianDate([calDate.year(), calDate.month(), day]);

    const key = thisDate.format("YYYY/MM/DD");

    const button = document.createElement("button");

    button.type = "button";
    button.className = "cal-day";
    button.textContent = day;

    const todayStart = new Date();
    todayStart.setHours(0, 0, 0, 0);

    const thisJsDate = thisDate.toDate();
    thisJsDate.setHours(0, 0, 0, 0);

    const isPast = thisJsDate < todayStart;

    const isToday = key === today.format("YYYY/MM/DD");

    if (isToday) {
      button.classList.add("today");
    }

    if (isPast) {
      button.classList.add("past");
      button.disabled = true;
    } else {
      button.classList.add("available");

      button.addEventListener("click", () => selectDate(key, thisDate, button));
    }

    if (key === selectedDateKey) {
      button.classList.add("selected");
    }

    daysEl.appendChild(button);
  }
}

// ==========================================
// SELECT DATE
// ==========================================

async function selectDate(key, pDateObj, button) {
  document
    .querySelectorAll(".cal-day.selected")
    .forEach((element) => element.classList.remove("selected"));

  button.classList.add("selected");

  selectedDateKey = key;

  hiddenTime.value = "";

  summaryEl.hidden = true;

  if (continueBtn) {
    continueBtn.hidden = true;
  }

  const weekday = getWeekdayName(pDateObj);

  timeBoxTitle.textContent = `ساعات خالی ${weekday} ${pDateObj.format("D MMMM")}`;

  timeSlotsEl.innerHTML = "<p>در حال دریافت زمان‌های خالی...</p>";

  timeBox.hidden = false;

  // Convert Persian date to Gregorian
  const jsDate = pDateObj.toDate();

  const year = jsDate.getFullYear();

  const month = String(jsDate.getMonth() + 1).padStart(2, "0");

  const day = String(jsDate.getDate()).padStart(2, "0");

  const backendDate = `${year}-${month}-${day}`;

  try {
    const availableTimes = await loadAvailableTimes(backendDate);

    timeSlotsEl.innerHTML = "";

    if (availableTimes.length === 0) {
      timeSlotsEl.innerHTML = "<p>زمان خالی برای این روز وجود ندارد.</p>";

      return;
    }

    availableTimes.forEach((time) => {
      const timeButton = document.createElement("button");

      timeButton.type = "button";
      timeButton.className = "time-slot";
      timeButton.textContent = time;

      timeButton.addEventListener("click", () =>
        selectTime(time, timeButton, weekday, pDateObj, backendDate),
      );

      timeSlotsEl.appendChild(timeButton);
    });
  } catch (error) {
    console.error("Availability error:", error);

    timeSlotsEl.innerHTML = `<p>${error.message}</p>`;
  }
}

// ==========================================
// SELECT TIME
// ==========================================

function selectTime(time, button, weekday, pDateObj, backendDate) {
  document
    .querySelectorAll(".time-slot.selected")
    .forEach((element) => element.classList.remove("selected"));

  selectedDate = backendDate;
  selectedTime = time;

  hiddenDate.value = backendDate;
  hiddenTime.value = time;

  // Save for next page
  localStorage.setItem("selectedDate", selectedDate);

  localStorage.setItem("selectedTime", selectedTime);

  summaryText.textContent = `نوبت شما: ${weekday} ${pDateObj.format("D MMMM")} ساعت ${time}`;

  summaryEl.hidden = false;

  if (continueBtn) {
    continueBtn.hidden = false;
  }
}

// ==========================================
// MONTH NAVIGATION
// ==========================================

document.getElementById("cal-prev").addEventListener("click", () => {
  calDate = calDate.subtract("month", 1);

  renderCalendar();
});

document.getElementById("cal-next").addEventListener("click", () => {
  calDate = calDate.add("month", 1);

  renderCalendar();
});

// ==========================================
// INIT
// ==========================================
renderCalendar();
if (window.lucide) {
  lucide.createIcons();
}
