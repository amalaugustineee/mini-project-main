from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app.models.charity import Charity
from app import db
from werkzeug.security import generate_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        
        # Simple validation
        if not username or not email or not password:
            flash('All fields are required.')
            return render_template('register.html')
            
        if password != password_confirm:
            flash('Passwords do not match.')
            return render_template('register.html')
            
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists.')
            return render_template('register.html')
            
        if User.query.filter_by(email=email).first():
            flash('Email already registered.')
            return render_template('register.html')
            
        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        
        # Add user to database
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.')
        return redirect(url_for('auth.login'))
        
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Validate input
        if not username or not password:
            flash('Please provide both username and password.')
            return render_template('login.html')
            
        # Find user by username
        user = User.query.filter_by(username=username).first()
        
        if user is None or not user.check_password(password):
            flash('Invalid username or password.')
            return render_template('login.html')
            
        # Log the user in
        login_user(user)
        next_page = request.args.get('next')
        
        if not next_page or next_page.startswith('/'):
            next_page = url_for('main.index')
            
        return redirect(next_page)
        
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))

@auth_bp.route('/profile')
@login_required
def profile():
    # Get blockchain data
    from app.blockchain.blockchain import get_blockchain
    blockchain = get_blockchain()
    
    # Get user's donation transactions
    user_transactions = []
    for block in blockchain.chain:
        for tx in block.transactions:
            if tx.transaction_type == 'donation' and tx.sender_id == current_user.id:
                # Find charity info
                charity = Charity.query.filter_by(blockchain_address=tx.recipient_id).first()
                if charity:
                    # Get charity's spending transactions
                    spending_transactions = blockchain.get_charity_spending(charity.blockchain_address)
                    
                    # Calculate total spent and current balance
                    total_spent = sum(stx.amount for stx in spending_transactions)
                    
                    donation_data = {
                        'transaction': tx,
                        'charity': charity,
                        'spending_transactions': spending_transactions,
                        'total_spent': total_spent,
                        'current_balance': charity.total_received - total_spent
                    }
                    user_transactions.append(donation_data)
    
    # Get all charities for linking in the UI
    charities = Charity.query.filter_by(admin_approved=True).all()
    
    return render_template('profile.html', 
                           user=current_user, 
                           transactions=user_transactions,
                           charities=charities) 