import streamlit as st

st.title("My First Streamlit App")
st.write("Hello, welcome to my first Streamlit application!")

#Text Components
st.title("This is a Title")
st.header("This is a Header")
st.subheader("This is a Subheader")
st.write("This is normal text.")
st.markdown("This is **Bold** text using Markdown.")

#Input Components
#Text Input
name=st.text_input("Enter your name:")
st.write(f"Hello, {name}!")

#Number Input
age=st.number_input("Enter your age:")
st.write("Your age is:", age)

#Buttons
if st.button("Click Me"):
    st.write("Button clicked!")

#Slider
number=st.slider("Pick a number:", 0, 100)
st.write("You picked: ", number)

#Selectbox
city=st.selectbox("Select your city:", ["Chennai", "Coimbatore", "Kochi", "Allepey"])
st.write("You selected: ", city)

#Checkbox
agree=st.checkbox("I agree to the terms and conditions")
if agree:
    st.write("Thank you for agreeing!")

#Showing Messages
st.success("This is a success message! (green).")
st.info("This is an info message! (blue).")
st.warning("This is a warning message! (yellow).")
st.error("This is an error message! (red).")
