from app import create_app, db
from app.models.user import User

def setup_admin():
    app = create_app()
    with app.app_context():
        # Create admin user if it doesn't exist
        admin = User.query.filter_by(email='admin@charitychain.com').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@charitychain.com',
                is_admin=True,
                simulated_token_balance=1000.0
            )
            admin.set_password('admin123')  # Change this password in production!
            db.session.add(admin)
            db.session.commit()
            print('Admin user created successfully!')
        else:
            print('Admin user already exists!')

if __name__ == '__main__':
    setup_admin() 