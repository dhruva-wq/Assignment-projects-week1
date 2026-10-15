"""Basic FastAPI app - CAIE Assignment 4

Run:   uvicorn main:app --reload
Docs:  http://127.0.0.1:8000/docs
"""
from fastapi import FastAPI

app = FastAPI(title="Basic FastAPI App", description="My first small API")


@app.get("/")
def read_root():
    """Root endpoint: returns a welcome message."""
    return {"message": "Hello, Dhruv! Welcome to my FastAPI app."}


@app.get("/greet/{name}")
def greet(name: str):
    """Path parameter: /greet/Dhruv -> {"greeting": "Hello, Dhruv!"}"""
    return {"greeting": f"Hello, {name}!"}


@app.get("/square")
def square(number: int = 0):
    """Query parameter with a default: /square?number=5 -> {"number": 5, "square": 25}
    If 'number' is missing, it falls back to 0; if it isn't an integer, FastAPI returns a 422 error.
    """
    return {"number": number, "square": number * number}