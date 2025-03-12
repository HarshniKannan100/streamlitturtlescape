import streamlit as st
import psycopg2
import pandas as pd
from datetime import datetime
import requests
from twilio.rest import Client
import os
from dotenv import load_dotenv
from streamlit_javascript import st_javascript  # For real GPS

    # Load environment variables
load_dotenv()

    # Twilio Credentials
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE = os.getenv("TWILIO_PHONE")

    # Initialize Twilio Client
client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

    # Database Connection
def connect_db():
    return psycopg2.connect(
        dbname="table1",
        user="postgres",
        password="root",
        host="localhost",
        port="5432"
    )

    # Function to Register Fisherman
def register_user(username, phone_number):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO fishermen (username, phone_number) VALUES (%s, %s)", (username, phone_number))
    conn.commit()
    cur.close()
    conn.close()

    # Function to Check Login
def check_login(username, phone_number):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM fishermen WHERE username=%s AND phone_number=%s", (username, phone_number))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user

    # Dummy GPS coordinates (Example: Chennai, India)
lat, lon = 38.39, 159.70  
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

st.write(f"📍 **Location:** {lat}, {lon} at {current_time}")

    # Display Map with Dummy Data
st.map(pd.DataFrame({"lat": [lat], "lon": [lon]}))

    # Streamlit UI
st.title("🐢 TurtleScape - AI Powered Turtle Protection System")

menu = st.sidebar.selectbox("Menu", ["Sign Up", "Login", "Dashboard"])

if menu == "Sign Up":
    st.subheader("📌 Register")
    username = st.text_input("Username")
    phone_number = st.text_input("Phone Number")

    if st.button("Register"):
        register_user(username, phone_number)
        st.success("✅ Registered successfully! Please log in.")

elif menu == "Login":
    st.subheader("🔑 Login")
    username = st.text_input("Username")
    phone_number = st.text_input("Phone Number")

    if st.button("Login"):
        if check_login(username, phone_number):
            st.session_state["user"] = username  # Store session
            st.success("✅ Login successful! Redirecting to Dashboard...")
        else:
            st.error("❌ Invalid credentials. Please register first.")

elif menu == "Dashboard":
    if "user" not in st.session_state:
        st.warning("⚠️ Please log in first.")
    else:
        st.subheader("📊 Fisherman Dashboard")
        st.write(f"👋 Welcome, {st.session_state['user']}!")

        

        if lat is None or lon is None:
            st.error("⚠️ Please enable GPS permissions.")
        else:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.write(f"📍 Your Location: {lat}, {lon} at {current_time}")

                # Display Map
            st.map(pd.DataFrame({"lat": [lat], "lon": [lon]}))

                # Dummy Risk Prediction (Replace with ML Model)
            risk_level = "High"

            st.write(f"🚨 **Risk Level:** {risk_level}")

                # Send Twilio Alert
            if risk_level == "High":
                try:
                    message = client.messages.create(
                        body=f"⚠️ High Risk Alert! Avoid the area: {lat}, {lon}",
                        from_=TWILIO_PHONE,
                        to=phone_number # type: ignore
                        )
                    st.success(f"🚨 Alert sent to {phone_number}") # type: ignore
                except Exception as e:
                    st.error(f"❌ Error sending alert: {str(e)}")
