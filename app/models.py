from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='Clerk')  # Roles: Admin, Manager, Clerk
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Security Helpers
    def set_password(self, password):
        """Hashes and sets user password using Bcrypt."""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Verifies plain password against stored hash."""
        return bcrypt.check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat()
        }


class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False, index=True)
    category = db.Column(db.String(50), nullable=True)
    batch_number = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    manufacture_date = db.Column(db.Date, nullable=True)
    expiry_date = db.Column(db.Date, nullable=False, index=True)
    status = db.Column(db.String(20), nullable=False, default='Fresh')  # Fresh, Expiring Soon, Expired
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship with alert logs
    alerts = db.relationship('AlertLog', backref='product', lazy=True, cascade='all, delete-orphan')

    def update_status(self):
        """Business logic to update product status based on current date."""
        today = datetime.utcnow().date()
        days_until_expiry = (self.expiry_date - today).days

        if days_until_expiry < 0:
            self.status = 'Expired'
        elif days_until_expiry <= 30:
            self.status = 'Expiring Soon'
        else:
            self.status = 'Fresh'

    def to_dict(self):
        return {
            'id': self.id,
            'product_name': self.product_name,
            'category': self.category,
            'batch_number': self.batch_number,
            'quantity': self.quantity,
            'manufacture_date': self.manufacture_date.isoformat() if self.manufacture_date else None,
            'expiry_date': self.expiry_date.isoformat(),
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }


class AlertLog(db.Model):
    __tablename__ = 'alert_logs'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    alert_date = db.Column(db.DateTime, default=datetime.utcnow)
    recipient_email = db.Column(db.String(120), nullable=False)
    alert_type = db.Column(db.String(30), nullable=False, default='Expiry Warning')
    status_sent = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product.product_name if self.product else None,
            'alert_date': self.alert_date.isoformat(),
            'recipient_email': self.recipient_email,
            'alert_type': self.alert_type,
            'status_sent': self.status_sent
        }