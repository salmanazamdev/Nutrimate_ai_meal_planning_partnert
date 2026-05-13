from flask import Flask, request, jsonify, render_template
import joblib
import pandas as pd
from recommender import get_recommendations

app = Flask(__name__)

# =========================
# LOAD MODEL
# =========================
try:
    model = joblib.load("meal_model.pkl")
    print("✅ ML Model Loaded")
except:
    model = None
    print("⚠️ Model not loaded")


# =========================
# LOAD DATASETS (SAFE ONCE)
# =========================
try:
    df1 = pd.read_excel("Datasets Nutrimate.xlsx")
    df2 = pd.read_excel("Datasets Nutrimate2.xlsx")

    df1.columns = df1.columns.str.strip().str.lower().str.replace(" ", "_")
    df2.columns = df2.columns.str.strip().str.lower().str.replace(" ", "_")

    print("✅ Datasets Loaded")
except Exception as e:
    df1 = pd.DataFrame()
    df2 = pd.DataFrame()
    print("⚠️ Dataset error:", e)


# =========================
# MEMORY DATABASE
# =========================
meals_db = []


# =========================
# ADD MEAL
# =========================
@app.route("/add_meal", methods=["POST"])
def add_meal():
    data = request.get_json()

    meal = {
        "id": len(meals_db) + 1,
        "name": data.get("name"),
        "mealType": data.get("mealType"),
        "calories": data.get("calories"),
        "protein": data.get("protein"),
        "cost": data.get("cost"),
        "date": data.get("date")
    }

    meals_db.append(meal)

    return jsonify({"success": True, "meal": meal})


# =========================
# DELETE MEAL
# =========================
@app.route("/delete_meal/<int:meal_id>", methods=["DELETE"])
def delete_meal(meal_id):
    global meals_db
    meals_db = [m for m in meals_db if m.get("id") != meal_id]
    return jsonify({"success": True})


# =========================
# CLEAR MEALS
# =========================
@app.route("/clear_meals", methods=["DELETE"])
def clear_meals():
    global meals_db
    date = request.args.get("date")

    meals_db = [m for m in meals_db if m.get("date") != date]
    return jsonify({"success": True})


# =========================
# FRONTEND ROUTES
# =========================
@app.route("/")
def welcome():
    return render_template("welcome.html")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/createaccount")
def createaccount():
    return render_template("createaccount.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/faq")
def faq():
    return render_template("faq.html")


@app.route("/howitworks")
def howitworks():
    return render_template("howitworks.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


# =========================
# CHAT API (DUAL DATASET SAFE)
# =========================
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json(silent=True)

        if not data:
            return jsonify({"success": False, "error": "No JSON received"})

        user_message = data.get("message", "").lower()

        # combine datasets safely
        df = pd.concat([df1, df2], ignore_index=True)

        if df.empty:
            return jsonify({"success": False, "error": "No dataset loaded"})

        if "meal" not in df.columns:
            return jsonify({"success": False, "error": "meal column missing"})

        results = df[
            df["meal"].astype(str)
            .str.lower()
            .str.contains(user_message, na=False)
        ]

        # fallback safe sample
        if results.empty:
            safe_df = df[df["meal"].notna()]
            if safe_df.empty:
                return jsonify({"success": False, "error": "No meals found"})
            results = safe_df.sample(1)

        meal = results.iloc[0].to_dict()

        return jsonify({
            "success": True,
            "meal": meal.get("meal", ""),
            "type": meal.get("type", ""),
            "calories": meal.get("calories", ""),
            "protein": meal.get("protein", ""),
            "carbs": meal.get("carbs", ""),
            "fats": meal.get("fats", ""),
            "goal": meal.get("goal", ""),
            "disease": meal.get("disease", ""),
            "bmi_level": meal.get("bmi_level", ""),
            "diet_type": meal.get("diet_type", ""),
            "meal_time": meal.get("meal_time", ""),
            "image": meal.get("image", ""),
            "image_prompt": meal.get("image_prompt", "")
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


# =========================
# PREDICT API
# =========================
@app.route("/predict", methods=["POST"])
def predict():
    try:

        if model is None:
            return jsonify({"success": False, "error": "Model not loaded"})

        data = request.get_json(silent=True)
        if not data:
            return jsonify({"success": False, "error": "No input data"})

        age = float(data.get("age") or 25)
        weight = float(data.get("weight") or 70)
        height = float(data.get("height") or 170)

        gender = data.get("gender") or "male"
        goal = data.get("goal") or "maintain"
        disease = data.get("disease") or "none"

        diet_type = data.get("dietType") or "omnivore"
        meal_time = data.get("meal_time") or "morning"

        height_m = height / 100 if height > 3 else height
        bmi = weight / (height_m ** 2)

        bmi_level = (
            "under" if bmi < 18.5 else
            "normal" if bmi < 25 else
            "over" if bmi < 30 else
            "obese"
        )

        input_df = pd.DataFrame([{
            "age": age,
            "weight": weight,
            "height": height_m,
            "gender": gender,
            "bmi": bmi,
            "goal": goal,
            "disease": disease,
            "bmi_level": bmi_level
        }])

        prediction = model.predict(input_df)

        recommendations = get_recommendations(
            goal=goal,
            disease=disease,
            diet_type=diet_type,
            meal_time=meal_time,
            use_ai_image=True
        )

        return jsonify({
            "success": True,
            "meal": str(prediction[0]),
            "bmi": round(bmi, 1),
            "bmi_level": bmi_level,
            "recommendations": recommendations
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


# =========================
# GET MEALS (SAFE)
# =========================
@app.route("/get_meals")
def get_meals():
    try:
        date = request.args.get("date")

        if not date:
            return jsonify({"success": False, "error": "Date required"})

        filtered = [m for m in meals_db if m.get("date") == date]

        return jsonify({"success": True, "data": filtered})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


# =========================
# DATASET MEALS
# =========================
@app.route("/dataset_meals")
def dataset_meals():
    try:
        goal = request.args.get("goal", "maintain")
        meal_time = request.args.get("meal_time", "morning")

        df = pd.concat([df1, df2], ignore_index=True)

        if df.empty:
            return jsonify({"success": False, "error": "Dataset empty"})

        if "goal" not in df.columns or "meal_time" not in df.columns:
            return jsonify({"success": False, "error": "Missing columns"})

        filtered = df[
            (df["goal"] == goal) &
            (df["meal_time"] == meal_time)
        ]

        if filtered.empty:
            return jsonify({"success": True, "data": []})

        meals = filtered.sample(min(5, len(filtered)))

        return jsonify({
            "success": True,
            "data": meals.to_dict(orient="records")
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


# =========================
# RUN SERVER
# =========================
if __name__ == "__main__":
    app.run(debug=True)