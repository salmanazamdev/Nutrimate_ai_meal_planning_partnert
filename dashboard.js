/* NutriMate Dashboard JS — CLEAN FLASK VERSION */
document.addEventListener("DOMContentLoaded", async () => {

  // ───────────────── AUTH CHECK ─────────────────
  if (typeof checkAuth === "function") {
    try { await checkAuth(true); } catch (e) {}
  }

  // ───────────────── ELEMENTS ─────────────────
  const todayMealsEl = document.getElementById("todayMeals");
  const planDateEl   = document.getElementById("planDate");
  const aiArea       = document.getElementById("aiSuggestions");

  if (planDateEl && !planDateEl.value) {
    planDateEl.value = new Date().toISOString().split("T")[0];
  }

  // ───────────────── TOTALS ─────────────────
  function updateTotals(meals = []) {
    const sum = (key) => meals.reduce((t, m) => t + (parseFloat(m[key]) || 0), 0);

    const set = (id, val) => {
      const el = document.getElementById(id);
      if (el) el.textContent = val;
    };

    set("totalCals", Math.round(sum("calories")));
    set("totalProtein", Math.round(sum("protein")));
    set("totalCost", sum("cost").toFixed(0));
  }

  // ───────────────── RENDER MEALS ─────────────────
  async function renderMeals() {
    if (!todayMealsEl) return;

    const date = planDateEl?.value || new Date().toISOString().split("T")[0];

    todayMealsEl.innerHTML = `<p>Loading...</p>`;

    try {
      const res = await fetch(`/get_meals?date=${date}`);
      const meals = await res.json();

      if (!Array.isArray(meals) || meals.length === 0) {
        todayMealsEl.innerHTML = `<p>No meals found</p>`;
        updateTotals([]);
        return;
      }

      todayMealsEl.innerHTML = meals.map(m => `
        <div class="meal-card">
          <div>
            <strong>${m.name || "Meal"}</strong>
            <small>${m.mealType || ""}</small>
          </div>

          <div class="stats">
            <span>${m.calories || 0} kcal</span>
            <span>${m.protein || 0}g</span>
            <span>Rs ${m.cost || 0}</span>
          </div>

          <button class="deleteMealBtn" data-id="${m.id}">✕</button>
        </div>
      `).join("");

      updateTotals(meals);

      <p><strong>Why this meal?</strong></p>

      document.querySelectorAll(".deleteMealBtn").forEach(btn => {
        btn.addEventListener("click", async () => {
          await fetch(`/delete_meal/${btn.dataset.id}`, { method: "DELETE" });
          renderMeals();
        });
      });

    } catch (err) {
      todayMealsEl.innerHTML = `<p>Error loading meals</p>`;
    }
  }

  renderMeals();

  if (planDateEl) {
    planDateEl.addEventListener("change", renderMeals);
  }

  // ───────────────── ADD MEAL ─────────────────
  const addBtn = document.getElementById("addCustomMealBtn");

  if (addBtn) {
    addBtn.addEventListener("click", async (e) => {
      e.preventDefault();

      const payload = {
        name: document.getElementById("searchMeal")?.value || "",
        mealSlot: document.getElementById("mealSlot")?.value || "Meal",
        calories: document.getElementById("mealCalories")?.value || 0,
        protein: document.getElementById("mealProtein")?.value || 0,
        cost: document.getElementById("mealCost")?.value || 0,
        date: planDateEl?.value
      };

      if (!payload.name) return alert("Enter meal name");

      await fetch("/add_meal", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      ["searchMeal","mealCalories","mealProtein","mealCost"].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = "";
      });

      renderMeals();
    });
  }

 
  // PROFILE BUTTON
const profileBtn = document.getElementById("profileBtn");

if (profileBtn) {
  profileBtn.addEventListener("click", () => {

    const profileData = {
      name: document.getElementById("name")?.value,
      age: document.getElementById("age")?.value,
      weight: document.getElementById("weight")?.value,
      height: document.getElementById("height")?.value
    };

    console.log("Profile Saved:", profileData);

    alert("Profile saved successfully!");
  });
}


// GOAL BUTTON
const goalBtn = document.getElementById("goalBtn");

if (goalBtn) {
  goalBtn.addEventListener("click", () => {

    const goalData = {
      goal: document.getElementById("goalType")?.value,
      calories: document.getElementById("calTarget")?.value,
      protein: document.getElementById("proteinTarget")?.value
    };

    console.log("Goals Saved:", goalData);

    alert("Goals saved successfully!");
  });
}


  // ───────────────── CLEAR DAY ─────────────────
  const clearBtn = document.getElementById("clearDayBtn");

  if (clearBtn) {
    clearBtn.addEventListener("click", async () => {
      const date = planDateEl?.value;
      await fetch(`/clear_meals?date=${date}`, { method: "DELETE" });
      renderMeals();
    });
  }

  // ───────────────── GOAL CALC ─────────────────
  const calcBtn = document.getElementById("calcGoalBtn");

  if (calcBtn) {
    calcBtn.addEventListener("click", () => {
      const weight = parseFloat(document.getElementById("weight")?.value) || 70;
      const activity = document.getElementById("activity")?.value || "moderate";
      const goal = document.getElementById("goalType")?.value || "maintain";

      const mult = {
        sedentary: 1.2,
        light: 1.375,
        moderate: 1.55,
        active: 1.725
      }[activity] || 1.55;

      let calories = weight * 24 * mult;
      if (goal === "loss") calories -= 300;
      if (goal === "gain") calories += 300;

      document.getElementById("calTarget").value = Math.round(calories);
      document.getElementById("proteinTarget").value = Math.round(weight * 1.6);
    });
  }

  // ───────────────── FIXED AI PREDICT (IMPORTANT FIX) ─────────────────
  const aiBtn = document.getElementById("suggestMealsBtn");

  if (aiBtn) {
    aiBtn.addEventListener("click", async (e) => {
      e.preventDefault();

      if (!aiArea) return;

      aiArea.innerHTML = "Generating AI meal...";

      const payload = {
        age: document.getElementById("age")?.value || 25,
        weight: document.getElementById("weight")?.value || 70,
        height: document.getElementById("height")?.value || 170,
        goal: document.getElementById("goalType")?.value || "maintain",
        activity: document.getElementById("activity")?.value || "moderate"
      };

      try {
        const res = await fetch("/predict", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });

        const data = await res.json();
<p>BMI: ${data.bmi}</p>
<p>Status: ${data.bmi_level}</p>
        if (data.status === "success") {
          aiArea.innerHTML = data.data.map(m => `
            <div class="ai-result">
              <h3>${m.meal}</h3>
              <p>${m.type}</p>
              <p>${m.calories} kcal</p>

              ${m.image_data?.image ? `<img src="${m.image_data.image}" width="150">` : ""}
            </div>
          `).join("");
        } else {
          aiArea.innerHTML = "No AI data found";
        }

      } catch (e) {
        aiArea.innerHTML = "AI not available";
      }
    });
  }

  // ───────────────── CHAT ─────────────────
  
  window.sendChat = async function () {

  const input = document.getElementById("chatInput");
  const box = document.getElementById("chatBox");

  if (!input.value.trim()) return;

  const userText = input.value;

  // USER MESSAGE
  box.innerHTML += `
    <div class="chat-msg user">
      ${userText}
    </div>
  `;

  input.value = "";

  try {

    const res = await fetch("/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        message: userText
      })
    });

    const data = await res.json();

    // BOT REPLY
    box.innerHTML += `
      <div class="chat-msg bot">
        Recommended Meal:
        ${data.data[0].meal}
      </div>
    `;

  } catch (e) {

    box.innerHTML += `
      <div class="chat-msg bot">
        AI unavailable
      </div>
    `;
  }
};

});