import pickle
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import numpy as np

# 1. Load the Model ONCE when the server starts
# We use a path relative to the project root to find the file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, 'fraud_model.pkl')

model =None
try:
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)
    print("✅ Model loaded successfully!")
except Exception as e:
    print(f"❌ Error loading model:{e}")
    model = None

# 2. The API View
@csrf_exempt  # Allows us to test easily without complex tokens
def predict_fraud(request):
    if request.method == 'GET':
        if model is None:
            return JsonResponse({'error': 'Model not loaded'},status =500)
        # Get 'amount' from the URL (e.g., ?amount=500)
        
        # Validation: Did they actually provide an amount?
        
        amount =request.GET.get('amount')

        if amount is None:
            return JsonResponse({'error':'Please provide amount. Example: ?amount=500'},status =400)
        try:
            val =float(amount)
            # --- FIX: CREATE 30 FEATURES INSTEAD OF 1 ---
            # We create a row of 30 zeros (representing Time, V1...V28, Amount)
            features = np.zeros((1, 30))
            
            # We put your input 'amount' into the last column (index 29)
            # (Assuming 'Amount' was the last column in your training data)
            features[0, 29] = val
            
            # Predict
            prediction = model.predict(features)[0]
            risk_score =model.predict_proba(features)[0][1]
            
            is_fraud =bool(prediction[0] ==1)
            result = "Fraudulent" if prediction[0] == 1 else "Legitimate"
            return JsonResponse({
                'status': 'success',
                'input_amount': val,
                'is_fraud': is_fraud,
                'message': "FRAUD DETECTED!" if is_fraud else "Transaction Legitimate",
                'risk_score': f"{risk_score:.4f}"
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Only GET requests are allowed'}, status=405)