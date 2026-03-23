from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory
import pandas as pd
import joblib
import os
import re

# ---------------- APP CONFIG ----------------
app = Flask(__name__)
app.secret_key = "ai_real_estate_secret_key_2024"

# ---------------- LOAD MODEL & DATA ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USER_FILE = os.path.join(BASE_DIR, "users_db.csv")
DATA_FILE = os.path.join(BASE_DIR, "gujarat_real_estate_properties.csv")
MODEL_FILE = os.path.join(BASE_DIR, "catboost_model(final).joblib")

df = pd.read_csv(DATA_FILE)
model = joblib.load(MODEL_FILE)

# ---------------- HELPERS ----------------
def load_users():
    if os.path.exists(USER_FILE):
        return pd.read_csv(USER_FILE, dtype=str)
    else:
        return pd.DataFrame(columns=["name", "mobile", "email", "password"])

def save_user(name, mobile, email, password):
    users = load_users()
    new_user = pd.DataFrame([[name, mobile, email, password]],
                            columns=["name", "mobile", "email", "password"])
    users = pd.concat([users, new_user], ignore_index=True)
    users.to_csv(USER_FILE, index=False)

def format_price(price):
    if price >= 1e7:
        return f"₹ {price/1e7:.2f} Cr"
    else:
        return f"₹ {price/1e5:.2f} L"

BHK_RANGES = {
    1: (300, 700),
    2: (600, 1200),
    3: (900, 1800),
    4: (1400, 2500),
    5: (1800, 4000)
}

# ---------------- AUTH ROUTES ----------------
@app.route("/")
def index():
    if session.get("logged_in"):
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    success = request.args.get("success")

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        if not (email and password):
            error = "Please enter both email and password"
        else:
            users = load_users()
            # Explicit warning if account doesn't exist
            if email not in users["email"].astype(str).str.strip().values:
                error = "Account not found. Please register first."
            else:
                user = users[
                    (users["email"].astype(str).str.strip() == email) &
                    (users["password"].astype(str).str.strip() == password)
                ]
                if not user.empty:
                    session["logged_in"] = True
                    session["user"] = user.iloc[0]["name"]
                    return redirect(url_for("dashboard"))
                else:
                    error = "Invalid password"

    return render_template("login.html", error=error, success=success, mode="login")

@app.route("/register", methods=["POST"])
def register():
    name = request.form.get("name", "").strip()
    mobile = request.form.get("mobile", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "").strip()

    if not (name and mobile and email and password):
        return render_template("login.html", error="All fields are required", mode="register")

    # Password strictness: at least one special character required
    if not re.search(r"[!@#$%^&*()_+={}\[\]|\\:;\"'<>,.?/`~-]", password):
        return render_template("login.html", error="Password must contain at least 1 special character", mode="register")

    users = load_users()
    if email in users["email"].values:
        return render_template("login.html", error="Email already registered", mode="register")

    save_user(name, mobile, email, password)
    return redirect(url_for("login", success="Registration successful! Please login"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    cities = sorted(df["city"].dropna().unique().tolist())
    max_area = int(df["area_sqft"].max())
    user_name = session.get("user", "")

    return render_template("dashboard.html",
                           cities=cities,
                           max_area=max_area,
                           user_name=user_name,
                           bhk_ranges=BHK_RANGES)

# ---------------- API ----------------
@app.route("/api/locations")
def api_locations():
    city = request.args.get("city", "")
    locations = sorted(df[df["city"] == city]["location"].dropna().unique().tolist())
    return jsonify(locations)

@app.route("/api/predict", methods=["POST"])
def api_predict():
    try:
        data = request.get_json()
        city = data["city"]
        location = data["location"]
        area_sqft = int(data["area_sqft"])
        bhk = int(data["bhk"])
        property_age = int(data["property_age"])
        parking = int(data.get("parking", 0))
        lift = int(data.get("lift", 0))
        balcony = int(data.get("balcony", 0))
        budget = data.get("budget")

        furnishing = "Unfurnished"

        # Validation
        min_area, max_area = BHK_RANGES.get(bhk, (200, 5000))
        if area_sqft < min_area or area_sqft > max_area:
            return jsonify({"error": f"Area should be between {min_area} and {max_area} sqft for {bhk} BHK"}), 400

        # Predict
        input_data = pd.DataFrame([[
            city, location, area_sqft, bhk, furnishing,
            property_age, parking, lift, balcony
        ]], columns=[
            "city", "location", "area_sqft", "bhk",
            "furnishing", "property_age",
            "parking", "lift", "balcony"
        ])

        prediction = float(model.predict(input_data)[0])
        lower = prediction * 0.9
        upper = prediction * 1.1
        price_sqft = prediction / area_sqft

        # Budget verdict
        verdict = None
        verdict_type = None
        if budget:
            budget = int(str(budget).replace(",", "").strip())
            if prediction > budget:
                verdict = "Property seems overpriced compared to your budget"
                verdict_type = "over"
            elif prediction < budget * 0.8:
                verdict = "Great deal! Well within your budget"
                verdict_type = "good"
            else:
                verdict = "Fair price — close to your budget"
                verdict_type = "fair"

        # Confidence
        if budget:
            diff_ratio = abs(prediction - budget) / budget
            confidence = int(max(70, min(95, 100 - diff_ratio * 100)))
        else:
            confidence = 85

        return jsonify({
            "prediction": format_price(prediction),
            "prediction_raw": prediction,
            "lower": format_price(lower),
            "upper": format_price(upper),
            "price_sqft": f"₹ {price_sqft:,.0f}",
            "verdict": verdict,
            "verdict_type": verdict_type,
            "confidence": confidence
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------- SERVE LOGO ----------------
@app.route("/logo")
def logo():
    return send_from_directory(BASE_DIR, "data_vidwan_logo.png.jpeg")

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True, port=5000)
