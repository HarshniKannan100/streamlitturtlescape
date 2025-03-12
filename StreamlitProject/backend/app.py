import argparse
import psycopg2
from datetime import datetime
import requests
from twilio.rest import Client
import os
from dotenv import load_dotenv
import joblib

# Load environment variables
load_dotenv()
model = joblib.load("turtle_risk_model2.pkl")

# Database Connection
def connect_db():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

# Register Fisherman
def register_user(username, phone_number):
    conn = connect_db()
    cur = conn.cursor()
    
    try:
        cur.execute("INSERT INTO fishermen (username, phone_number) VALUES (%s, %s)", (username, phone_number))
        conn.commit()
        print("✅ User registered successfully!")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        cur.close()
        conn.close()

# Login Fisherman
def login_user(username, phone_number):
    conn = connect_db()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM fishermen WHERE username=%s AND phone_number=%s", (username, phone_number))
    user = cur.fetchone()
    
    cur.close()
    conn.close()

    if user:
        print("✅ Login successful!")
    else:
        print("❌ Invalid credentials.")

# Get Location
def get_location(lat, lon):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"📍 Location: {lat}, {lon} at {current_time}")

# Predict Risk
def predict_risk(username, phone_number, lat, lon):
    # Dummy Risk Prediction Logic
    risk_level = "High" if float(lat) > 50 else "Low"

    # Twilio Alert for High Risk
    if risk_level == "High":
        client = Client(os.getenv("TWILIO_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
        message = client.messages.create(
            body=f"⚠️ High Risk Alert! Avoid the area: {lat}, {lon}",
            from_=os.getenv("TWILIO_PHONE"),
            to=phone_number
        )
        print(f"🚨 Alert sent to {phone_number}")

    print(f"Risk Level: {risk_level}")

# Command Line Interface
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TurtleScape Command-Line Interface")
    parser.add_argument("action", choices=["register", "login", "location", "predict"], help="Choose an action")
    parser.add_argument("--username", help="Fisherman's username")
    parser.add_argument("--phone", help="Fisherman's phone number")
    parser.add_argument("--lat", help="Latitude")
    parser.add_argument("--lon", help="Longitude")

    args = parser.parse_args()

    if args.action == "register":
        if args.username and args.phone:
            register_user(args.username, args.phone)
        else:
            print("❌ Username and phone number required for registration.")

    elif args.action == "login":
        if args.username and args.phone:
            login_user(args.username, args.phone)
        else:
            print("❌ Username and phone number required for login.")

    elif args.action == "location":
        if args.lat and args.lon:
            get_location(args.lat, args.lon)
        else:
            print("❌ Latitude and longitude required for location.")

    elif args.action == "predict":
        if args.username and args.phone and args.lat and args.lon:
            predict_risk(args.username, args.phone, args.lat, args.lon)
        else:
            print("❌ Username, phone number, latitude, and longitude required for risk prediction.")
