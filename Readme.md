# 🛡️ SentinelAI: Real-Time Machine Learning Fraud Detection System

**SentinelAI** is a production-grade, decoupled Full-Stack web application designed to identify and analyze credit card fraud in real time. The system exposes a highly responsive **Django REST API** serving a serialized machine learning model, backed by database transaction logging and a modern **Vanilla JS Glassmorphism Dashboard** displaying rich interactive charts and live API metrics.

---

## 📄 ATS-Friendly Resume Bullets
*Copy and customize this section directly for your internship or job search:*

* **Engineered** an end-to-end decoupled Full-Stack Fraud Detection System integrating a Scikit-Learn Logistic Regression model with a Django REST API backend and a responsive Vanilla Javascript frontend.
* **Designed and implemented** database transaction logging and aggregation REST endpoints, reducing frontend dashboard loading states by querying and summarizing raw transaction histories on-the-fly.
* **Trained and serialized** an ML classification model on Kaggle's Credit Card Fraud dataset (284,807 transactions), optimizing predictions across 30 features (PCA components + amount) to achieve **99.92% accuracy**, **88.30% precision**, and **82.60% F1-score**.
* **Developed** an interactive monitoring dashboard with dark/light themes featuring live SVG/Chart.js trends, risk distributions, a transaction simulator, and a **dynamic API round-trip latency tracker** (averaging ~10ms).

---

## 🛠️ System Architecture & Stack

```
   ┌──────────────────────────────────────────────┐
   │             Vanilla JS Frontend              │
   │  (Glassmorphism Dashboard, Charts, Latency)   │
   └──────────────────────┬───────────────────────┘
                          │ HTTP REST API
                          ▼ (Fetch API, JSON)
   ┌──────────────────────────────────────────────┐
   │             Django REST Backend              │
   │      (Views, URL Routing, CORS Headers)      │
   └─────────────┬──────────────────┬─────────────┘
                 │                  │
                 ▼ Load Model       ▼ Write / Read Logs
   ┌──────────────────────────┐   ┌───────────────────────┐
   │   Scikit-Learn Model     │   │    SQLite Database    │
   │ (Serialized .pkl Binary) │   │ (Transaction Schema)  │
   └──────────────────────────┘   └───────────────────────┘
```

* **Frontend:** HTML5, CSS3 Variables (Custom Glassmorphism styling, Dark/Light theme switcher), Vanilla JavaScript, Chart.js (CDN)
* **Backend:** Python, Django 5.2+, `django-cors-headers`
* **Machine Learning:** Scikit-Learn (Logistic Regression), Pandas, NumPy, Pickle
* **Database:** SQLite (Relational transaction logs)

---

## 📊 Machine Learning Model Details

* **Dataset Source:** Kaggle Credit Card Fraud Detection Dataset
* **Data Scale:** 284,807 transaction records (highly imbalanced: 492 fraud occurrences, 0.172% of total data)
* **Features:** 30 features (1 `Time` feature, 28 PCA-reduced features `V1-V28`, and 1 `Amount` feature)
* **Algorithm:** Logistic Regression (scikit-learn)

### 📈 Baseline Model Performance Metrics
| Metric | Score | Note |
| :--- | :--- | :--- |
| **Accuracy** | **99.92%** | High baseline due to extreme class imbalance |
| **Precision** | **88.30%** | Minimizes false positive alerts for legitimate transactions |
| **Recall** | **77.60%** | Effectively captures a high portion of actual fraudulent acts |
| **F1-Score** | **82.60%** | Balanced harmonic mean optimizing both precision and recall |

---

## 🔌 API Documentation

### 1. Analyze Transaction (Predict)
* **Endpoint:** `POST /api/predict/` (supports `GET` fallback via `?amount=value`)
* **Request Body:**
  ```json
  {
    "amount": 1250.00
  }
  ```
* **Response:**
  ```json
  {
    "status": "success",
    "transaction_id": 42,
    "timestamp": "2026-06-07T13:02:14.456Z",
    "input_amount": 1250.00,
    "is_fraud": false,
    "message": "Transaction Legitimate",
    "risk_score": "0.1432"
  }
  ```

### 2. Transaction Log History
* **Endpoint:** `GET /api/transactions/`
* **Query Params:** `page` (default `1`), `limit` (default `20`), `is_fraud` (`true`/`false`), `min_amount` (float), `max_amount` (float)
* **Response:**
  ```json
  {
    "status": "success",
    "total_count": 250,
    "page": 1,
    "limit": 10,
    "transactions": [
      {
        "id": 250,
        "timestamp": "2026-06-07T12:58:30Z",
        "amount": 284.15,
        "risk_score": 0.052,
        "is_fraud": false
      }
    ]
  }
  ```

### 3. Aggregated Analytics Statistics
* **Endpoint:** `GET /api/stats/`
* **Response:** Returns summary data (`total_count`, `total_amount`, `fraud_count`, `avg_risk`, `fraud_rate`), bucketed risk distribution scores (10 slots), and daily fraud/volume trends over the past 30 days.

### 4. Database Historical Seeder
* **Endpoint:** `POST /api/seed/`
* **Request Body:**
  ```json
  {
    "count": 250,
    "clear": true
  }
  ```
* **Response:** Seeds realistic random transaction metadata and runs them through the serialized classifier model to populate database logs over the past 30 days.

---

## 🚀 How to Run Locally

### 1. Start the Django API Backend
1. Open your terminal in the project directory.
2. Activate the virtual environment:
   ```powershell
   # Windows PowerShell
   venv\Scripts\Activate.ps1
   ```
3. Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
4. Run standard Django migrations:
   ```bash
   python manage.py migrate
   ```
5. Launch the backend server:
   ```bash
   python manage.py runserver
   ```
   The backend will be live on `http://127.0.0.1:8000/`.

### 2. Launch the Dashboard Frontend
1. Open the [index.html](file:///C:/Fraud_Detection/index.html) file directly in any web browser (or serve it using a lightweight dev server on Port 5500).
2. Click the **Seed 250 Historical Records** button in the control panel to generate historical transaction data.
3. Switch between Dark/Light themes, search the logs, and run simulated manual transactions to observe live updates.