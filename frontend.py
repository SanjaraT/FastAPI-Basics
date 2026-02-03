import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/predict"
#Page
st.set_page_config(
    page_title="Insurance Risk Predictor",
    layout="centered"
)

st.title("Insurance Risk Prediction")
st.write("Enter the details below and click **Predict**")

#User Inputs
age = st.number_input("Age", min_value=1, max_value=100, value=25)

weight = st.number_input("Weight (kg)", min_value=20.0, max_value=200.0, value=70.0)

height = st.number_input("Height (meters)", min_value=1.0, max_value=2.5, value=1.65)

income_lpa = st.number_input("Income (LPA)", min_value=0.0, max_value=100.0, value=5.0)

smoker = st.selectbox("Smoker?", ["No", "Yes"])
smoker = True if smoker == "Yes" else False

city = st.text_input("City", value="Indore")

occupation = st.selectbox(
    "Occupation",
    ['retired', 'freelancer', 'student', 'government_job', 'business_owner',
 'unemployed', 'private_job']
)

#Button
if st.button("Predict"):
    payload = {
        "age": age,
        "weight": weight,
        "height": height,
        "income_lpa": income_lpa,
        "smoker": smoker,
        "city": city,
        "occupation": occupation
    }

    try:
        response = requests.post(
            "http://127.0.0.1:8000/predict",
            json=payload
        )

        if response.status_code == 200:
            result = response.json()
         
            prediction = result.get("predicted_category", "Unknown")

            if prediction == "Low":
                st.success("LOW")
            elif prediction == "Medium":
                st.warning("MEDIUM")
            elif prediction == "High":
                st.error("HIGH")
            else:
                st.info(f"Prediction: {prediction}")

        else:
            st.error("API Error")
            st.write(response.text)

    except Exception as e:
        st.error("Could not connect to FastAPI server")
        st.write(e)