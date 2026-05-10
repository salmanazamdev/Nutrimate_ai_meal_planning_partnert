from email import policy

from flask import Flask, request, jsonify, render_template
import joblib
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


# HOME / WELCOME PAGE
@app.route("/")
def welcome():
    return render_template("welcome.html")


# LOGIN PAGE
@app.route("/login")
def login():
    return render_template("login.html")


# DASHBOARD PAGE
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

    data = request.get_json()

    age = float(data.get("age", 25))
    weight = float(data.get("weight", 70))
    height_cm = float(data.get("height", 170))
    goal = data.get("goal", "maintain").lower()


    # BMI
    height_m = height_cm / 100
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

    # smart meal time
    meal_time = "morning"

    # dynamic recommendation
    result = get_recommendations(
        goal=goal,
        disease="none",
        diet_type="vegan",
        meal_time=meal_time,
        use_ai_image=True
    )

    return jsonify({
        "status": "success",
        "bmi": round(bmi, 1),
        "bmi_level": bmi_level,
        "data": result
    })

# =========================
# 🤖 CHAT API
# =========================
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    msg = data.get("message", "").lower()

    goal = "gain" if "protein" in msg else "loss" if "diet" in msg else "maintain"

    result = get_recommendations(goal, "none", "vegan", "morning")

    return jsonify({
        "status": "success",
        "data": result
    })


#get_meals

@app.route("/get_meals")
def get_meals():
    date = request.args.get("date")

    return jsonify([
        {
            "id": 1,
            "name": "Oats",
            "mealType": "Breakfast",
            "calories": 250,
            "protein": 10,
            "cost": 50
        }
    ])
# =========================
# RUN SERVER
# =========================
if __name__ == "__main__":
    app.run(debug=True)