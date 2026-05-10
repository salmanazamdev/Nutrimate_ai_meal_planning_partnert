import os

# =========================
# ⚙️ PERFORMANCE FIX (IMPORTANT)
# =========================
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

from image_generator import generate_image
import pandas as pd
import numpy as np


# =========================
# 📦 LOAD DATASET (ROBUST)
# =========================
def load_dataset(path):

    df = pd.read_excel(path)

    # normalize columns
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    # fallback for broken header
    if "meal" not in df.columns:
        df = pd.read_excel(path, header=None)
        df.columns = [
            "meal", "type", "calories", "protein", "carbs", "fats",
            "goal", "disease", "bmi_level", "diet_type", "meal_time",
            "image", "image_prompt"
        ]

    df = df.drop_duplicates().fillna("none")

    # normalize text columns
    text_cols = ["meal", "goal", "disease", "diet_type", "meal_time"]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.lower().str.strip()

    # numeric fix
    num_cols = ["calories", "protein", "carbs", "fats"]
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    print("✅ Dataset Loaded Successfully")
    print("📊 Columns:", df.columns.tolist())

    return df


df = load_dataset("Datasets Nutrimate2.xlsx")


# =========================
# 🍽️ SMART RECOMMENDER ENGINE
# =========================
def recommend_meals(goal, disease, diet_type, meal_time, top_n=5):

    data = df.copy()

    goal = goal.lower().strip()
    disease = disease.lower().strip()
    diet_type = diet_type.lower().strip()
    meal_time = meal_time.lower().strip()

    # safe filtering (no crash ever)
    if "goal" in data.columns:
        data = data[data["goal"] == goal]

    if "diet_type" in data.columns:
        data = data[data["diet_type"] == diet_type]

    if "meal_time" in data.columns:
        data = data[data["meal_time"] == meal_time]

    if "disease" in data.columns and disease != "none":
        data = data[(data["disease"] == disease) | (data["disease"] == "none")]

    # remove duplicates
    if "meal" in data.columns:
        data = data.drop_duplicates(subset=["meal"])

    # scoring system (AI ranking)
    if not data.empty:
        data["score"] = (
            data["protein"] * 2
            - data["calories"] * 0.01
            - data["fats"] * 0.3
            + np.random.rand(len(data)) * 0.2
        )

        data = data.sort_values(by="score", ascending=False)

    else:
        data = df.sample(min(top_n, len(df)))

    return data.head(top_n)


# =========================
# 🤖 WHY THIS MEAL ENGINE
# =========================
def explain_meal(row):

    reasons = []

    if row["protein"] >= 20:
        reasons.append("High protein supports muscle growth")

    if row["calories"] <= 300:
        reasons.append("Low calories help weight control")

    if row["fats"] <= 15:
        reasons.append("Healthy low-fat option")

    if str(row["diet_type"]).lower() == "vegan":
        reasons.append("Plant-based vegan friendly")

    if str(row["goal"]).lower() == "loss":
        reasons.append("Supports fat loss goal")

    return reasons if reasons else ["Balanced nutritious meal"]


# =========================
# 🖼️ IMAGE ENGINE (HYBRID)
# =========================
def get_image(row, use_ai=False):

    image_path = row.get("image", "none.jpg")
    prompt = row.get("image_prompt", "")

    # dataset mode
    if not use_ai:
        return {
            "mode": "dataset",
            "image": image_path,
            "prompt": prompt
        }

    # AI mode (future integration)
    try:
        ai_image = generate_image(prompt)
        if ai_image:
            image_path = ai_image
    except Exception as e:
        print("⚠️ AI image failed:", e)

    return {
        "mode": "ai",
        "image": image_path,
        "prompt": prompt
    }


# =========================
# 🔥 MAIN API FUNCTION (FLASK READY)
# =========================
def get_recommendations(goal, disease, diet_type, meal_time, use_ai_image=False):

    meals = recommend_meals(goal, disease, diet_type, meal_time)

    results = []

    for _, row in meals.iterrows():

        results.append({
            "meal": row["meal"],
            "type": row["type"],
            "calories": float(row["calories"]),
            "protein": float(row["protein"]),
            "carbs": float(row["carbs"]),
            "fats": float(row["fats"]),

            "goal": row["goal"],
            "disease": row["disease"],
            "diet_type": row["diet_type"],
            "meal_time": row["meal_time"],

            # image system
            "image_data": get_image(row, use_ai=use_ai_image),

            # AI explanation
            "why": explain_meal(row)
        })

    return results


# =========================
# 🧪 TEST RUN
# =========================
if __name__ == "__main__":

    output = get_recommendations(
        goal="loss",
        disease="none",
        diet_type="vegan",
        meal_time="morning",
        use_ai_image=False
    )

    print("\n🔥 FINAL OUTPUT:\n")

    for r in output:
        print("Meal:", r["meal"])
        print("Type:", r["type"])
        print("Calories:", r["calories"])
        print("Image:", r["image_data"]["image"])
        print("Prompt:", r["image_data"]["prompt"])
        print("Why:", r["why"])
        print("-" * 60)