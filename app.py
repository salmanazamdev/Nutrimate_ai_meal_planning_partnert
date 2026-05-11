from flask import Flask, request, jsonify, render_template
import joblib
import pandas as pd
from recommender import get_recommendations

app = Flask(__name__)

# =========================
# LOAD ML MODEL
# =========================
try:
    model = joblib.load("meal_model.pkl")
    print("✅ ML Model Loaded")
except:
    model = None
    print("⚠️ ML Model not loaded")


# =========================
# 🌐 FRONTEND PAGES
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
# 🔥 AI RECOMMENDER API
# =========================

@app.route("/predict", methods=["POST"])
def predict():
    try:

        if model is None:
            return jsonify({
                "success": False,
                "error": "Model not loaded. Run main.py first."
            })

        data = request.get_json()

        # User Inputs
        age = float(data.get("age", 25))
        weight = float(data.get("weight", 70))
        height = float(data.get("height", 170))
        gender = data.get("gender", "male")
        goal = data.get("goal", "maintain").lower()
        disease = data.get("disease", "none")

        # Height convert cm -> meter
        if height > 3:
            height_m = height / 100
        else:
            height_m = height

        # BMI
        bmi = weight / (height_m ** 2)

        # BMI Level
        if bmi < 18.5:
            bmi_level = "under"
        elif bmi < 25:
            bmi_level = "normal"
        elif bmi < 30:
            bmi_level = "over"
        else:
            bmi_level = "obese"

        bmi_age = bmi * age

        # Model Input
        input_df = pd.DataFrame([{
            "age": age,
            "weight": weight,
            "height": height_m,
            "gender": gender,
            "bmi": bmi,
            "goal": goal,
            "disease": disease,
            "bmi_level": bmi_level,
            "bmi_age": bmi_age
        }])

        # Prediction
        prediction = model.predict(input_df)

        # Recommendation
        recommendations = get_recommendations(
            goal=goal,
            disease=disease,
            diet_type="vegan",
            meal_time="morning",
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
        return jsonify({
            "success": False,
            "error": str(e)
        })


# =========================
# 🤖 CHAT API
# =========================

@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()
    msg = data.get("message", "").lower()

    if "protein" in msg:
        goal = "gain"
    elif "diet" in msg:
        goal = "loss"
    else:
        goal = "maintain"

    result = get_recommendations(
        goal,
        "none",
        "vegan",
        "morning"
    )

    return jsonify({
        "status": "success",
        "data": result
    })


# =========================
# 🍽 GET MEALS API
# =========================

@app.route("/get_meals")
def get_meals():

    goal = request.args.get("goal", "maintain")
    meal_time = request.args.get("meal_time", "morning")

    # Dataset load
    df = pd.read_csv("meals_dataset.csv")

    # Filter
    filtered = df[
        (df["goal"] == goal) &
        (df["meal_time"] == meal_time)
    ]

    # Random meals
    meals = filtered.sample(min(5, len(filtered)))

    # JSON convert
    result = meals.to_dict(orient="records")

    return jsonify(result)


# =========================
# RUN SERVER
# =========================

if __name__ == "__main__":
    app.run(debug=True)