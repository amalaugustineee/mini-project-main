from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from app.models.charity import Charity
from app.models.user import User
from app import db
from app.blockchain.blockchain import get_blockchain
import functools

charity_auth_bp = Blueprint('charity_auth', __name__)

# Decorator for charity login required
def charity_login_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'charity_id' not in session:
            flash('Please log in as a charity to access this page.')
            return redirect(url_for('charity_auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@charity_auth_bp.route('/charity/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Validate input
        if not email or not password:
            flash('Please provide both email and password.')
            return render_template('charity_auth/login.html')
            
        # Find charity by email
        charity = Charity.query.filter_by(email=email).first()
        
        if charity is None or not charity.check_password(password) or not charity.admin_approved:
            flash('Invalid email/password or charity not approved yet.')
            return render_template('charity_auth/login.html')
            
        # Log the charity in by setting session value
        session['charity_id'] = charity.id
        charity.is_authenticated = True
        db.session.commit()
        
        flash(f'Welcome, {charity.name}! You are now logged in as a charity.')
        return redirect(url_for('charity_auth.dashboard'))
        
    return render_template('charity_auth/login.html')

@charity_auth_bp.route('/charity/logout')
@charity_login_required
def logout():
    charity_id = session.pop('charity_id', None)
    
    if charity_id:
        charity = Charity.query.get(charity_id)
        if charity:
            charity.is_authenticated = False
            db.session.commit()
    
    flash('You have been logged out of your charity account.')
    return redirect(url_for('main.index'))

@charity_auth_bp.route('/charity/dashboard')
@charity_login_required
def dashboard():
    # Get current charity
    charity = Charity.query.get(session['charity_id'])
    
    # Get blockchain data
    blockchain = get_blockchain()
    
    # Get all donations received by this charity
    donations = []
    for block in blockchain.chain:
        for tx in block.transactions:
            if tx.transaction_type == 'donation' and tx.recipient_id == charity.blockchain_address:
                # For each donation, find the donor name
                donor = User.query.get(tx.sender_id)
                donor_name = donor.username if donor else "Unknown User"
                
                donation_data = {
                    'donor_name': donor_name,
                    'donor_id': tx.sender_id,
                    'amount': tx.amount,
                    'timestamp': tx.timestamp,
                    'transaction_id': tx.id
                }
                donations.append(donation_data)
    
    # Get spending transactions
    spending_transactions = blockchain.get_charity_spending(charity.blockchain_address)
    
    # Calculate totals
    total_donations = charity.total_received
    total_spent = sum(tx.amount for tx in spending_transactions)
    current_balance = total_donations - total_spent
    
    return render_template('charity_auth/dashboard.html', 
                           charity=charity,
                           donations=donations,
                           spending_transactions=spending_transactions,
                           total_donations=total_donations,
                           total_spent=total_spent,
                           current_balance=current_balance)

@charity_auth_bp.route('/charity/spend', methods=['GET', 'POST'])
@charity_login_required
def spend_funds():
    # Get current charity
    charity = Charity.query.get(session['charity_id'])
    
    # Get blockchain
    blockchain = get_blockchain()
    
    # Calculate available balance
    spending_transactions = blockchain.get_charity_spending(charity.blockchain_address)
    total_spent = sum(tx.amount for tx in spending_transactions)
    available_balance = charity.total_received - total_spent
    
    if request.method == 'POST':
        try:
            amount = float(request.form.get('amount'))
            purpose = request.form.get('purpose')
            recipient = request.form.get('recipient')
            
            # Validate input
            if amount <= 0:
                flash('Please enter a positive amount.')
                return render_template('charity_auth/spend.html', charity=charity, available_balance=available_balance)
                
            if amount > available_balance:
                flash(f'Insufficient funds. Available balance: {available_balance} SIM Tokens')
                return render_template('charity_auth/spend.html', charity=charity, available_balance=available_balance)
                
            if not purpose or not recipient:
                flash('Please provide both purpose and recipient details.')
                return render_template('charity_auth/spend.html', charity=charity, available_balance=available_balance)
            
            # Format purpose/recipient for blockchain transaction
            spending_description = f"{purpose} - {recipient}"
            
            # Create blockchain transaction for the spending
            transaction = blockchain.add_transaction(
                charity.blockchain_address,
                spending_description,
                amount,
                'spending'
            )
            
            # Mine pending transactions
            blockchain.mine_pending_transactions()
            
            flash(f'Successfully recorded spending of {amount} SIM Tokens for {purpose}.')
            return redirect(url_for('charity_auth.dashboard'))
            
        except (ValueError, TypeError):
            flash('Please ensure all fields are filled correctly.')
            return render_template('charity_auth/spend.html', charity=charity, available_balance=available_balance)
    
    return render_template('charity_auth/spend.html', charity=charity, available_balance=available_balance)

@charity_auth_bp.route('/charity/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        email = request.form.get('email')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        
        # Simple validation
        if not name or not email or not description or not password:
            flash('All fields are required.')
            return render_template('charity_auth/register.html')
            
        if password != password_confirm:
            flash('Passwords do not match.')
            return render_template('charity_auth/register.html')
            
        # Check if charity with this email already exists
        if Charity.query.filter_by(email=email).first():
            flash('Email already registered for a charity.')
            return render_template('charity_auth/register.html')
            
        # Create new charity 
        charity = Charity(name=name, description=description, email=email)
        charity.set_password(password)
        charity.admin_approved = False  # Require admin approval
        
        # Add charity to database
        db.session.add(charity)
        db.session.commit()
        
        flash('Thank you for registering! Your charity account is pending admin approval.')
        return redirect(url_for('charity_auth.login'))
        
    return render_template('charity_auth/register.html') 