from app import db
import datetime
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash

class Charity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    blockchain_address = db.Column(db.String(64), unique=True, nullable=False)
    admin_approved = db.Column(db.Boolean, default=False)
    total_received = db.Column(db.Float, default=0.0)  # Running total of donations received
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    # Authentication fields
    email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(128))
    is_authenticated = db.Column(db.Boolean, default=False)  # For charity login tracking
    
    def __init__(self, name, description, email=None, admin_approved=False):
        self.name = name
        self.description = description
        self.email = email
        self.admin_approved = admin_approved
        # Generate a blockchain address using a hash of name and timestamp
        address_string = f"{name}-{datetime.datetime.utcnow().timestamp()}"
        self.blockchain_address = hashlib.sha256(address_string.encode()).hexdigest()[:64]
    
    def set_password(self, password):
        """Set password hash for charity login"""
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        """Check password for charity login"""
        return check_password_hash(self.password_hash, password) 