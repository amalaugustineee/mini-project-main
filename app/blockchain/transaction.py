import hashlib
import time
import json

class Transaction:
    def __init__(self, sender_id, recipient_id, amount, transaction_type):
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        self.amount = amount
        self.timestamp = time.time()
        self.transaction_type = transaction_type  # 'donation' or 'spending'
        self.id = self._calculate_hash()
        
    def _calculate_hash(self):
        """
        Create a unique hash for this transaction
        """
        transaction_string = json.dumps({
            'sender_id': str(self.sender_id),
            'recipient_id': str(self.recipient_id),
            'amount': float(self.amount),
            'timestamp': float(self.timestamp),
            'transaction_type': str(self.transaction_type)
        }, sort_keys=True)
        
        return hashlib.sha256(transaction_string.encode()).hexdigest()
    
    def to_dict(self):
        """
        Return transaction data as a dictionary
        """
        return {
            'id': self.id,
            'sender_id': self.sender_id,
            'recipient_id': self.recipient_id,
            'amount': self.amount,
            'timestamp': self.timestamp,
            'transaction_type': self.transaction_type
        } 