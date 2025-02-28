import numpy as np
import pickle
import hashlib
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
import mysql.connector
from mysql.connector import Error
import joblib
import pandas as pd

app = Flask(__name__)
app.secret_key = 'Santosh@366'  # Change this to a strong secret key

# 🔹 Load ML Models (Crop & Fertilizer)
try:
    crop_model = pickle.load(open('model.pkl', 'rb'))
    print("✅ Crop Model loaded successfully!")
except Exception as e:
    print(f"❌ Error loading crop model: {e}")

# Load the trained fertilizer model and encoders
try:
    with open("fertilizer_model.pkl", "rb") as file:
        fertilizer_data = pickle.load(file)
        model = fertilizer_data["model"]
        print("Expected feature names:", model.feature_names_in_)
        le_fertilizer = fertilizer_data["le_fertilizer"]
        le_soil = fertilizer_data["le_soil"]
        le_crop = fertilizer_data["le_crop"]

    print("✅ Fertilizer Model loaded successfully!")
except Exception as e:
    print(f"❌ Error loading fertilizer model: {e}")


# 🔹 Database Connection Function
def get_db_connection():
    try:
        print("🔄 Trying to connect to MySQL...")  # Debugging message
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Santosh@366",
            database="flask_db",
            port=3306,
            connection_timeout=5,
            use_pure=True  # Force pure Python mode
        )
        if conn.is_connected():
            print("✅ Database connected successfully!")
            return conn
    except Error as e:
        print(f"❌ Database connection failed! Error: {e}")  # Show exact error
        return None

# 🔹 Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about1.html')

@app.route('/crop')
def crop():
    return render_template('crop.html')

@app.route('/fertilizer')
def fertilizer():
    return render_template('fertilizer.html')

@app.route('/review')
def review():
    return render_template('feedback.html')  # Make sure you have feedback.html

@app.route('/contact')
def contact():
    return render_template('contact.html')  # Make sure you have contact.html

@app.route('/logout1')
def logout1():
    session.clear()
    flash("ℹ️ You have been logged out.", "info")
    return redirect(url_for('option'))  # Redirect to the option page

@app.route('/logout2')
def logout2():
    session.clear()  # Clears all session data
    return redirect(url_for('home'))  # Redirects to the home page

# 🔹 Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()

        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM users WHERE email = %s AND password = %s"
            cursor.execute(query, (email, password))
            user = cursor.fetchone()
            cursor.close()
            connection.close()

            if user:
                session['user_id'] = user['id']
                session['name'] = user['name']
                flash("✅ Login successful!", "success")
                return redirect(url_for('option'))
            else:
                flash("❌ Invalid email or password!", "danger")
                return redirect(url_for('login'))
        else:
            flash("❌ Database connection failed!", "danger")
            return redirect(url_for('login'))

    return render_template('login.html')

# 🔹 Registration Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        mobile_no = request.form['mobile_no']
        address = request.form['address']
        gender = request.form['gender']
        email = request.form['email']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()

        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            try:
                # Check if the email already exists
                cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
                existing_user = cursor.fetchone()
                if existing_user:
                    flash("❌ Email already registered! Please log in.", "danger")
                    return redirect(url_for('login'))

                query = "INSERT INTO users (name, mobile_no, address, gender, email, password) VALUES (%s, %s, %s, %s, %s, %s)"
                cursor.execute(query, (name, mobile_no, address, gender, email, password))
                connection.commit()
                flash("✅ Registration successful! Please log in.", "success")
                return redirect(url_for('login'))
            except mysql.connector.Error as e:
                flash(f"❌ Database Error: {e}", "danger")
                return redirect(url_for('register'))
            finally:
                cursor.close()
                connection.close()
        else:
            flash("❌ Failed to connect to the database.", "danger")
            return redirect(url_for('register'))

    return render_template('Registration.html')

@app.route('/option')
def option():
    if 'user_id' not in session:
        flash("⚠️ Please log in first!", "warning")
        return redirect(url_for('login'))
    return render_template('option.html', name=session['name'])

@app.route('/logout')
def logout():
    session.clear()
    flash("ℹ️ You have been logged out.", "info")
    return redirect(url_for('home'))

# 🔹 Crop Prediction Route
@app.route('/predict', methods=['POST'])
def predict():
    try:
        int_features = [int(x) for x in request.form.values()]
        final_features = [np.array(int_features)]
        prediction = crop_model.predict(final_features)
        output = prediction[0]
        return render_template('crop.html', prediction_text=f'Suggested crop: "{output}".')
    except ValueError as ve:
        flash(f"❌ Value Error: {ve}", "danger")
    except Exception as e:
        flash(f"❌ Prediction error: {e}", "danger")
    return redirect(url_for('home'))

# 🔹 Fertilizer Prediction Route
@app.route('/predict_fertilizer', methods=['POST'])
def predict_fertilizer():
    try:
        # Get input values
        ph = float(request.form['ph'])
        soil_color = request.form['Soil_color']
        nitrogen = float(request.form['nitrogen'])
        phosphorus = float(request.form['phosphorus'])
        potassium = float(request.form['potassium'])
        crop = request.form['Crop']

        # Encode soil color & crop type (modify according to your encoding)
        soil_color_mapping = {'red': 0, 'black': 1, 'brown': 2, 'yellow': 3, 'other': 4}
        crop_mapping = {'wheat': 0, 'rice': 1, 'maize': 2, 'barley': 3, 'other': 4}

        soil_color_encoded = soil_color_mapping.get(soil_color, 4)  # Default to 'other' if not found
        crop_encoded = crop_mapping.get(crop, 4)

        # Create input DataFrame
        input_df = pd.DataFrame([[soil_color_encoded, nitrogen, phosphorus, potassium, ph, crop_encoded]],
                                columns=['Soil_color', 'Nitrogen', 'Phosphorus', 'Potassium', 'pH', 'Crop'])

        # Predict fertilizer (returns a number)
        prediction = model.predict(input_df)[0]

        # Convert prediction number to a meaningful fertilizer name
        fertilizer_mapping = {
            0: "Urea",
            1: "DAP",
            2: "MOP",
            3: "Super Phosphate",
            4: "Organic Manure",
            5: "Ammonium Sulfate"
        }

        recommended_fertilizer = fertilizer_mapping.get(prediction, "Unknown Fertilizer")

        return render_template('fertilizer.html', result=recommended_fertilizer)

    except Exception as e:
        return f"❌ Error: {str(e)}", 400
    
# API Endpoint for Crop Prediction
@app.route('/predict_api', methods=['POST'])
def predict_api():
    try:
        data = request.get_json(force=True)
        prediction = crop_model.predict([np.array(list(data.values()))])
        output = prediction[0]
        return jsonify({"prediction": output})
    except ValueError as ve:
        return jsonify({"error": f"Value Error: {ve}"})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
