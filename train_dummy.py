import pickle
import numpy as np
from sklearn.linear_model import LogisticRegression

print("🤖 Waking up the AI...")

# 1. Create Mock Data (30 columns to match your project)
# We generate 100 examples of "fake transactions"
X = np.random.rand(100, 30)
y = np.random.randint(0, 2, 100) # 0 = Legit, 1 = Fraud

# 2. Train the Brain (The "fit" step you were missing)
print("🧠 Training the brain...")
model = LogisticRegression()
model.fit(X, y)

# 3. Save to file (This "writes" the binary file for you)
print("💾 Saving fraud_model.pkl...")
with open('fraud_model.pkl', 'wb') as f:
    pickle.dump(model, f)
print("✅ DONE! You now have a working model file.")