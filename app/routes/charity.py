from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models.charity import Charity
from app.models.user import User
from app import db
from app.blockchain.blockchain import get_blockchain

charity_bp = Blueprint('charity', __name__)

@charity_bp.route('/charities')
def charities_list():
    # Get sort parameter (default to name)
    sort_by = request.args.get('sort', 'name')
    
    # Get approved charities with sorting
    if sort_by == 'donations':
        charities = Charity.query.filter_by(admin_approved=True).order_by(Charity.total_received.desc()).all()
    else:  # Default to sorting by name
        charities = Charity.query.filter_by(admin_approved=True).order_by(Charity.name).all()
        
    return render_template('charities.html', charities=charities, current_sort=sort_by)

@charity_bp.route('/charity/<int:charity_id>')
def charity_detail(charity_id):
    # Get charity by ID
    charity = Charity.query.get_or_404(charity_id)
    
    # Get charity's spending transactions
    blockchain = get_blockchain()
    spending_transactions = blockchain.get_charity_spending(charity.blockchain_address)
    
    return render_template('charity_detail.html', 
                           charity=charity,
                           spending_transactions=spending_transactions)

@charity_bp.route('/donate/<int:charity_id>', methods=['GET', 'POST'])
@login_required
def donate(charity_id):
    charity = Charity.query.get_or_404(charity_id)
    
    if request.method == 'POST':
        try:
            amount = float(request.form.get('amount'))
            
            # Validate donation amount
            if amount <= 0:
                flash('Please enter a positive donation amount.')
                return redirect(url_for('charity.charity_detail', charity_id=charity.id))
                
            if amount > current_user.simulated_token_balance:
                flash('Insufficient balance for this donation.')
                return redirect(url_for('charity.charity_detail', charity_id=charity.id))
                
            # Update user balance
            current_user.simulated_token_balance -= amount
            
            # Update charity's total received
            charity.total_received += amount
            
            # Create blockchain transaction
            blockchain = get_blockchain()
            transaction = blockchain.add_transaction(
                current_user.id,
                charity.blockchain_address,
                amount,
                'donation'
            )
            
            # Mine transactions (in real app this would be a background task)
            blockchain.mine_pending_transactions()
            
            # Save changes to database
            db.session.commit()
            
            flash(f'Successfully donated {amount} SIM Tokens to {charity.name}!')
            return redirect(url_for('charity.charity_detail', charity_id=charity.id))
            
        except ValueError:
            flash('Please enter a valid donation amount.')
            return redirect(url_for('charity.charity_detail', charity_id=charity.id))
            
    return render_template('donate.html', charity=charity) 