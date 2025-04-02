from app.models.charity import Charity
from app.models.user import User
from app import db

def seed_charities():
    """
    Add initial charity data to the database if no charities exist
    """
    # Check if there are already charities in the database
    existing_count = Charity.query.count()
    if existing_count > 0:
        return False  # Skip seeding if charities already exist
    
    # List of charities to create
    charities = [
        {
            "name": "Global Education Fund",
            "description": "Supporting educational initiatives in underserved communities worldwide. We provide school supplies, fund teacher training, and build educational infrastructure where it's needed most.",
            "email": "education@example.org",
            "password": "education123"
        },
        {
            "name": "Clean Water Initiative",
            "description": "Providing clean drinking water to communities in need by building wells, water filtration systems, and educating communities on water conservation and sanitation practices.",
            "email": "water@example.org",
            "password": "water123"
        },
        {
            "name": "Food Security Alliance",
            "description": "Fighting hunger through sustainable agriculture programs, food banks, and nutrition education. We work to ensure that vulnerable populations have consistent access to healthy food.",
            "email": "food@example.org",
            "password": "food123"
        },
        {
            "name": "Medical Relief International",
            "description": "Delivering essential healthcare services and medical supplies to disaster areas and communities with limited access to healthcare. We operate mobile clinics and train local healthcare workers.",
            "email": "medical@example.org",
            "password": "medical123"
        },
        {
            "name": "Wildlife Conservation Trust",
            "description": "Protecting endangered species and their habitats through conservation efforts, anti-poaching initiatives, and public education programs about biodiversity preservation.",
            "email": "wildlife@example.org",
            "password": "wildlife123"
        },
        {
            "name": "Renewable Energy Project",
            "description": "Promoting sustainable energy solutions in developing regions by implementing solar, wind, and other renewable energy technologies to reduce carbon footprint and increase energy access.",
            "email": "energy@example.org",
            "password": "energy123"
        },
        {
            "name": "Digital Literacy Foundation",
            "description": "Bridging the digital divide by providing technology access and education to underserved communities, with a focus on giving children and adults the digital skills needed in today's world.",
            "email": "digital@example.org",
            "password": "digital123"
        }
    ]
    
    # Create and add each charity
    for charity_data in charities:
        charity = Charity(
            name=charity_data["name"],
            description=charity_data["description"],
            email=charity_data["email"]
        )
        charity.set_password(charity_data["password"])
        charity.admin_approved = True  # Auto-approve seed charities
        db.session.add(charity)
    
    # Commit changes
    db.session.commit()
    
    return True  # Successfully seeded

def seed_admin_user():
    """
    Create an admin user if none exists
    """
    # Check if admin user already exists
    admin_exists = User.query.filter_by(is_admin=True).first()
    if admin_exists:
        return False  # Skip if admin already exists
    
    # Create admin user
    admin = User(
        username="admin",
        email="admin@charitychain.org",
        is_admin=True,
        simulated_token_balance=1000.0  # Give admin extra tokens
    )
    admin.set_password("admin123")  # Default password, should be changed in production
    
    # Add to database
    db.session.add(admin)
    db.session.commit()
    
    return True  # Successfully created admin 