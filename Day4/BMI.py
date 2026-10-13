import streamlit as st

#1. Title
st.title("BMI Calculator")
st.write("Enter your weight and height to calculate your Body Mass Index (BMI).")

#2. Get user input for weight and height
weight = st.number_input("Enter your weight in kilograms (KG):", min_value=1.0)
height = st.number_input("Enter your height in meters (Meters):", min_value=0.1)

#3. Buttons to Calculate BMI
if st.button("Calculate BMI"):
    bmi = weight / (height * height)
    st.write("Your BMI is: ", round(bmi, 2))

#4. Give a message based on BMI value
    if bmi < 18.5:
            st.warning("You are underweight.")
    elif 18.5 <= bmi < 25:
            st.success("You have a normal weight.")
    elif 25 <= bmi < 30:
            st.warning("You are overweight.")
    else:
        st.error("You are obese.")
