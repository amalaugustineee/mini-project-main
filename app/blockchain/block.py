import hashlib
import time
import json

class Block:
    def __init__(self, index, timestamp, transactions, previous_hash, nonce=0):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions  # List of Transaction objects
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.calculate_hash()
        
    def calculate_hash(self):
        """
        Calculate SHA-256 hash of the block
        """
        # Convert transactions to dictionaries for hashing
        transaction_dicts = [tx.to_dict() for tx in self.transactions]
        
        block_string = json.dumps({
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': transaction_dicts,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce
        }, sort_keys=True)
        
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def mine_block(self, difficulty):
        """
        Simplified mining process (Proof of Work)
        """
        target = '0' * difficulty
        
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()
            
        print(f"Block #{self.index} mined. Hash: {self.hash}")
        return True
        
    def to_dict(self):
        """
        Return block data as a dictionary
        """
        return {
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': [tx.to_dict() for tx in self.transactions],
            'previous_hash': self.previous_hash,
            'nonce': self.nonce,
            'hash': self.hash
        } 