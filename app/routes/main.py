from flask import Blueprint, render_template, current_app
from app.models.charity import Charity
from app import db

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # Get approved charities for homepage
    charities = Charity.query.filter_by(admin_approved=True).all()
    return render_template('index.html', charities=charities) 