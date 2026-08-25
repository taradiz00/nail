// Prevent empty links
document.querySelectorAll('a[href="#"]').forEach((link) => {
  link.addEventListener("click", (e) => {
    e.preventDefault();
  });
});

// Animation observer
const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.animate(
        [
          { opacity: 0, transform: "translateY(40px)" },
          { opacity: 1, transform: "translateY(0px)" },
        ],
        {
          duration: 700,
          fill: "forwards",
        },
      );
    }
  });
});

document.querySelectorAll(".crystal-card").forEach((card) => {
  observer.observe(card);
});

const selections = {
  hand: null,
  feet: null,
  design: false,
};

const serviceNames = {
  hand: "خدمات دست",
  feet: "خدمات پا",
  design: "خدمات طراحی",
};
const serviceIds = {
  hand: {
    "کاشت یا ترمیم": 1,
  },

  feet: {
    "کاشت یا ترمیم": 2,
  },

  design: 3,
};

function getSelectedServiceIds() {
  const ids = [];

  if (selections.hand) {
    ids.push(serviceIds.hand[selections.hand]);
  }

  if (selections.feet) {
    ids.push(serviceIds.feet[selections.feet]);
  }

  if (selections.design) {
    ids.push(serviceIds.design);
  }

  return ids.filter(Boolean);
}
/* =========================
   HAND + FEET
========================= */

document.querySelectorAll(".selectable-card").forEach((card) => {
  const service = card.dataset.service;
  const status = card.querySelector(".card-status");

  card.addEventListener("click", (e) => {
    if (e.target.closest(".service-option")) return;

    card.classList.toggle("open");
  });

  card.querySelectorAll(".service-option").forEach((option) => {
    option.addEventListener("click", (e) => {
      e.stopPropagation();

      const value = option.dataset.value;

      /* clicking selected option again removes it */

      if (option.classList.contains("active")) {
        option.classList.remove("active");

        selections[service] = null;

        card.classList.remove("selected");

        status.textContent = "انتخاب نوع خدمات";

        updateSummary();

        return;
      }

      /* remove previous selection */

      card
        .querySelectorAll(".service-option")
        .forEach((btn) => btn.classList.remove("active"));

      /* select new option */

      option.classList.add("active");

      selections[service] = value;

      card.classList.add("selected");

      status.textContent = value;

      updateSummary();
    });
  });
});

/* =========================
   DESIGN
========================= */

const designCard = document.querySelector(".design-card");

if (designCard) {
  designCard.addEventListener("click", () => {
    selections.design = !selections.design;

    designCard.classList.toggle("selected", selections.design);

    const status = designCard.querySelector(".card-status");

    status.textContent = selections.design
      ? "انتخاب شده ✓"
      : "برای انتخاب کلیک کنید";

    updateSummary();
  });
}

/* =========================
   UPDATE SUMMARY
========================= */

function updateSummary() {
  const container = document.getElementById("selected-services");
  const continueBtn = document.getElementById("continue-btn");

  if (!container || !continueBtn) return;

  container.innerHTML = "";

  let selectedCount = 0;

  if (selections.hand) {
    selectedCount++;

    container.innerHTML += `
      <div class="selected-service-item">
        <span>${serviceNames.hand}</span>
        <span>${selections.hand}</span>
      </div>
    `;
  }

  if (selections.feet) {
    selectedCount++;

    container.innerHTML += `
      <div class="selected-service-item">
        <span>${serviceNames.feet}</span>
        <span>${selections.feet}</span>
      </div>
    `;
  }

  if (selections.design) {
    selectedCount++;

    container.innerHTML += `
      <div class="selected-service-item">
        <span>${serviceNames.design}</span>
        <span>انتخاب شده</span>
      </div>
    `;
  }

  if (selectedCount === 0) {
    container.innerHTML = `
      <p class="empty-selection">
        هنوز خدماتی انتخاب نکرده‌اید.
      </p>
    `;

    continueBtn.classList.add("disabled");
    return;
  }

  const total = selectedCount * 200000;

  container.innerHTML += `
    <div class="summary-total">
      <span>جمع بیعانه</span>
      <strong>${total.toLocaleString("fa-IR")} تومان</strong>
    </div>
  `;

  continueBtn.classList.remove("disabled");
}

const continueBtn = document.getElementById("continue-btn");

if (continueBtn) {
  continueBtn.addEventListener("click", (event) => {
    event.preventDefault();

    const selectedServiceIds = getSelectedServiceIds();

    if (selectedServiceIds.length === 0) {
      alert("لطفاً حداقل یک خدمت انتخاب کنید.");
      return;
    }

    localStorage.setItem(
      "selectedServiceIds",
      JSON.stringify(selectedServiceIds),
    );

    window.location.href = "calendar.html";
  });
}
lucide.createIcons();
