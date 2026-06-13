import pickle
import os
import json
import random
import numpy as np
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Sum, Avg, Count, Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from api.models import Transaction

# 1. Load the Model ONCE when the server starts
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, 'fraud_model.pkl')

model = None
try:
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)
    print("[Success] Model loaded successfully!")
except Exception as e:
    print(f"[Error] Error loading model: {e}")
    model = None

# 2. The API View (handles GET and POST)
@csrf_exempt
def predict_fraud(request):
    if model is None:
        return JsonResponse({'error': 'Model not loaded'}, status=500)

    amount = None
    custom_timestamp = None

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            amount = data.get('amount')
            custom_timestamp = data.get('timestamp')
        except Exception:
            return JsonResponse({'error': 'Invalid JSON body'}, status=400)
    elif request.method == 'GET':
        amount = request.GET.get('amount')
    else:
        return JsonResponse({'error': 'Only GET and POST requests are allowed'}, status=405)

    if amount is None:
        return JsonResponse({'error': 'Please provide amount. Example: ?amount=500'}, status=400)

    try:
        val = float(amount)
        # We create a row of 30 columns (representing Time, V1...V28, Amount)
        features = np.zeros((1, 30))
        features[0, 29] = val
        
        # Predict
        prediction = model.predict(features)[0]
        risk_score = float(model.predict_proba(features)[0][1])
        
        # Handle shape mismatch or list values gracefully
        try:
            is_fraud = bool(prediction[0] == 1)
        except (TypeError, IndexError):
            is_fraud = bool(prediction == 1)

        # Handle custom timestamp if provided (useful for seeding historical data)
        if custom_timestamp:
            try:
                if isinstance(custom_timestamp, str):
                    timestamp = datetime.fromisoformat(custom_timestamp.replace('Z', '+00:00'))
                else:
                    timestamp = custom_timestamp
            except ValueError:
                timestamp = timezone.now()
        else:
            timestamp = timezone.now()

        # Save to database
        tx = Transaction.objects.create(
            timestamp=timestamp,
            amount=val,
            risk_score=risk_score,
            is_fraud=is_fraud,
            features_json=json.dumps(features.tolist())
        )

        return JsonResponse({
            'status': 'success',
            'transaction_id': tx.id,
            'timestamp': tx.timestamp.isoformat(),
            'input_amount': val,
            'is_fraud': is_fraud,
            'message': "FRAUD DETECTED!" if is_fraud else "Transaction Legitimate",
            'risk_score': f"{risk_score:.4f}"
        })
        
    except ValueError:
        return JsonResponse({'error': 'Invalid amount value. Must be a number.'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# 3. Get Paginated Transactions History
def get_transactions(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Only GET requests are allowed'}, status=405)

    try:
        txs = Transaction.objects.all().order_by('-timestamp')
        
        # Filters
        is_fraud_param = request.GET.get('is_fraud')
        if is_fraud_param is not None:
            is_fraud_val = is_fraud_param.lower() in ['true', '1', 'yes']
            txs = txs.filter(is_fraud=is_fraud_val)
            
        min_amount = request.GET.get('min_amount')
        if min_amount is not None:
            txs = txs.filter(amount__gte=float(min_amount))
            
        max_amount = request.GET.get('max_amount')
        if max_amount is not None:
            txs = txs.filter(amount__lte=float(max_amount))

        # Pagination
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 20))
        start = (page - 1) * limit
        end = start + limit
        
        total_count = txs.count()
        txs_slice = txs[start:end]
        
        tx_list = []
        for t in txs_slice:
            tx_list.append({
                'id': t.id,
                'timestamp': t.timestamp.isoformat(),
                'amount': t.amount,
                'risk_score': round(t.risk_score, 4),
                'is_fraud': t.is_fraud
            })
            
        return JsonResponse({
            'status': 'success',
            'total_count': total_count,
            'page': page,
            'limit': limit,
            'transactions': tx_list
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# 4. Get Statistics Aggregations for Charts
def get_stats(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Only GET requests are allowed'}, status=405)

    try:
        total_count = Transaction.objects.count()
        if total_count == 0:
            return JsonResponse({
                'status': 'success',
                'summary': {
                    'total_count': 0,
                    'total_amount': 0.0,
                    'fraud_count': 0,
                    'avg_risk': 0.0,
                    'fraud_rate': 0.0
                },
                'risk_distribution': [0] * 10,
                'daily_trends': []
            })

        aggregates = Transaction.objects.aggregate(
            total_amt=Sum('amount'),
            fraud_cnt=Count('id', filter=Q(is_fraud=True)),
            avg_rk=Avg('risk_score')
        )
        
        total_amount = aggregates['total_amt'] or 0.0
        fraud_count = aggregates['fraud_cnt'] or 0
        avg_risk = aggregates['avg_rk'] or 0.0
        fraud_rate = (fraud_count / total_count) * 100 if total_count > 0 else 0.0

        # Risk Distribution in 10 buckets (0.0-0.1, 0.1-0.2, ...)
        risk_distribution = [0] * 10
        all_risks = Transaction.objects.values_list('risk_score', flat=True)
        for score in all_risks:
            bucket = min(int(score * 10), 9)  # 1.0 falls into index 9
            risk_distribution[bucket] += 1

        # Daily Trends for last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)
        daily_data = Transaction.objects.filter(timestamp__gte=thirty_days_ago) \
            .extra(select={'day': "date(timestamp)"}) \
            .values('day') \
            .annotate(
                total=Count('id'),
                fraud=Count('id', filter=Q(is_fraud=True)),
                total_vol=Sum('amount')
            ).order_by('day')
            
        daily_trends = []
        for day_stat in daily_data:
            daily_trends.append({
                'date': day_stat['day'],
                'total_count': day_stat['total'],
                'fraud_count': day_stat['fraud'],
                'total_volume': float(day_stat['total_vol'] or 0.0),
                'fraud_rate': round((day_stat['fraud'] / day_stat['total']) * 100, 2)
            })

        return JsonResponse({
            'status': 'success',
            'summary': {
                'total_count': total_count,
                'total_amount': float(total_amount),
                'fraud_count': fraud_count,
                'avg_risk': round(avg_risk, 4),
                'fraud_rate': round(fraud_rate, 2)
            },
            'risk_distribution': risk_distribution,
            'daily_trends': daily_trends
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# 5. Seed Historical Data (Developer Endpoint)
@csrf_exempt
def seed_transactions(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)
    
    if model is None:
        return JsonResponse({'error': 'Model not loaded'}, status=500)

    try:
        # Clear existing data if requested
        data = {}
        if request.body:
            try:
                data = json.loads(request.body)
            except Exception:
                pass
        
        if data.get('clear', False):
            Transaction.objects.all().delete()
            
        count_to_seed = int(data.get('count', 250))
        
        now = timezone.now()
        seeded_count = 0
        
        # We will distribute transactions over the last 30 days
        for i in range(count_to_seed):
            # Pick a random day in the last 30 days
            days_offset = random.randint(0, 30)
            hours_offset = random.randint(0, 23)
            minutes_offset = random.randint(0, 59)
            seconds_offset = random.randint(0, 59)
            
            tx_time = now - timedelta(
                days=days_offset,
                hours=hours_offset,
                minutes=minutes_offset,
                seconds=seconds_offset
            )
            
            # Generate amount (90% small regular transactions, 10% larger)
            if random.random() < 0.90:
                amount = round(random.uniform(5.0, 150.0), 2)
            else:
                amount = round(random.uniform(200.0, 6000.0), 2)
                
            # Create a 30-feature vector
            features = np.zeros((1, 30))
            features[0, 29] = amount
            
            # Introduce some random variation in feature columns to simulate model behavior
            # In a real model, high-risk amount transactions or odd values have higher risk
            if amount > 2000.0:
                # Add some feature variance that could trigger fraud
                features[0, 1:29] = np.random.randn(28) * 1.5
            else:
                features[0, 1:29] = np.random.randn(28) * 0.2
                
            # Predict using our actual loaded model
            prediction = model.predict(features)[0]
            risk_score = float(model.predict_proba(features)[0][1])
            
            # Handle index shape safely
            try:
                is_fraud = bool(prediction[0] == 1)
            except (TypeError, IndexError):
                is_fraud = bool(prediction == 1)
            
            # Force occasional fraud for high amounts to make charts interesting
            if amount > 4500.0 and random.random() < 0.6:
                is_fraud = True
                risk_score = max(risk_score, 0.85)

            Transaction.objects.create(
                timestamp=tx_time,
                amount=amount,
                risk_score=risk_score,
                is_fraud=is_fraud,
                features_json=json.dumps(features.tolist())
            )
            seeded_count += 1
            
        return JsonResponse({
            'status': 'success',
            'message': f'Successfully seeded {seeded_count} transactions.',
            'count': seeded_count
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)