from django.db import models

class Transaction(models.Model):
    timestamp = models.DateTimeField(db_index=True)
    amount = models.FloatField()
    risk_score = models.FloatField()
    is_fraud = models.BooleanField()
    features_json = models.TextField(default="[]")  # Store PCA feature list as JSON string

    def __str__(self):
        return f"Tx {self.id} - ${self.amount} (Fraud: {self.is_fraud})"
