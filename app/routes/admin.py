from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from app.models.charity import Charity
from app.models.user import User
from app import db
from app.blockchain.blockchain import get_blockchain
from app.utils.decorators import admin_required

admin_bp = Blueprint('admin', __name__)

# Admin role decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You do not have permission to access this page.')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    # Get pending charities
    pending_charities = Charity.query.filter_by(admin_approved=False).all()
    
    # Get approved charities
    approved_charities = Charity.query.filter_by(admin_approved=True).all()
    
    return render_template('admin/dashboard.html',
                         pending_charities=pending_charities,
                         approved_charities=approved_charities)

@admin_bp.route('/admin/charity/review/<int:charity_id>', methods=['GET'])
@login_required
@admin_required
def review_charity(charity_id):
    charity = Charity.query.get_or_404(charity_id)
    return render_template('admin/charity_review.html', charity=charity)

@admin_bp.route('/admin/approve_charity/<int:charity_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def approve_charity(charity_id):
    charity = Charity.query.get_or_404(charity_id)
    charity.admin_approved = True
    db.session.commit()
    
    flash(f'Charity {charity.name} has been approved.')
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/admin/reject_charity/<int:charity_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def reject_charity(charity_id):
    charity = Charity.query.get_or_404(charity_id)
    charity_name = charity.name
    db.session.delete(charity)
    db.session.commit()
    
    flash(f'Charity {charity_name} has been rejected and removed from the system.')
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/admin/create_charity', methods=['GET', 'POST'])
@login_required
@admin_required
def create_charity():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        if not name or not description:
            flash('Please provide both name and description.')
            return render_template('admin/create_charity.html')
            
        # Create new charity
        charity = Charity(
            name=name,
            description=description,
            admin_approved=True  # Auto-approve since admin is creating it
        )
        db.session.add(charity)
        db.session.commit()
        
        flash(f'Charity {name} has been created.')
        return redirect(url_for('admin.admin_dashboard'))
        
    return render_template('admin/create_charity.html')

@admin_bp.route('/admin/mine_blockchain')
@login_required
@admin_required
def mine_blockchain():
    blockchain = get_blockchain()
    blockchain.mine_pending_transactions()
    flash('Successfully mined pending transactions.')
    return redirect(url_for('admin.admin_dashboard')) 