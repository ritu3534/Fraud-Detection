# 🛡️ AI-Powered Fraud Detection System

## 📌 Overview
This project is an end-to-end, decoupled Full-Stack web application that uses a Machine Learning model to detect fraudulent financial transactions in real-time. 

Rather than leaving the predictive model in a Jupyter Notebook, I engineered a solution that serves the trained ML model through a **Django REST API** and consumes it via a lightweight, asynchronous **JavaScript frontend**.

## 🚀 Features
* **Real-time REST API:** A Django backend that accepts transaction data via HTTP GET requests and returns JSON risk scores.
* **Machine Learning Integration:** Uses a serialized `.pkl` Scikit-Learn model for instant predictions without retraining.
* **Decoupled Architecture:** Clean separation of concerns between the client interface (Port 5500) and the server processing (Port 8000).
* **CORS Configured:** Secure Cross-Origin Resource Sharing middleware implemented to allow seamless communication between isolated environments.

## 🛠️ Tech Stack
* **Backend:** Python, Django, `django-cors-headers`
* **Machine Learning:** Scikit-Learn, Pandas, Pickle
* **Frontend:** HTML5, CSS3, Vanilla JavaScript (Fetch API, async/await)

## ⚙️ How to Run Locally

### 1. Start the Backend API
Open your terminal and navigate to the backend directory:
```bash
# Ensure you are in your virtual environment
# Install required dependencies
pip install django django-cors-headers scikit-learn pandas

# Start the Django development server
python manage.py runserver