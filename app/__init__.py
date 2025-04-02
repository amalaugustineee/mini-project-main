from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

# Initialize SQLAlchemy
db = SQLAlchemy()

# Initialize login manager
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-simulation')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///charity_chain.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Ensure instance folder exists and has correct permissions
    os.makedirs(app.instance_path, exist_ok=True)
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    
    # Register custom Jinja filters
    from app.utils import register_filters
    register_filters(app)
    
    # Import and register blueprints
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.charity import charity_bp
    from app.routes.blockchain import blockchain_bp
    from app.routes.admin import admin_bp
    from app.routes.charity_auth import charity_auth_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(charity_bp)
    app.register_blueprint(blockchain_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(charity_auth_bp)
    
    # Create database tables
    with app.app_context():
        db_path = os.path.join(app.instance_path, 'charity_chain.db')
        # Ensure the database file has the correct permissions if it exists
        if os.path.exists(db_path):
            try:
                # Set permissions to allow read and write
                os.chmod(db_path, 0o664)  # Owner and group can read/write, others can read
            except Exception as e:
                print(f"Warning: Unable to set database file permissions: {e}")
        
        db.create_all()
        
        # Initialize blockchain (optional, could also be loaded from disk)
        from app.blockchain.blockchain import init_blockchain
        init_blockchain()
        
        # Seed initial charity data
        from app.utils.seed_data import seed_charities, seed_admin_user
        seed_charities()
        seed_admin_user()
    
    return app 