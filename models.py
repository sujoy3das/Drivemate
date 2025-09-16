from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
from itsdangerous import URLSafeTimedSerializer
from flask import current_app

db = SQLAlchemy()

# --- Association Objects for Sharing with Permissions ---
class UserFileShare(db.Model):
    __tablename__ = 'user_file_share'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey('file.id', ondelete='CASCADE'), primary_key=True)
    reshared_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    can_download = db.Column(db.Boolean, default=False, nullable=False)
    can_reshare = db.Column(db.Boolean, default=False, nullable=False)
    can_copy = db.Column(db.Boolean, default=False, nullable=False)

    user = db.relationship('User', foreign_keys=[user_id], back_populates='file_shares')
    file = db.relationship('File', back_populates='user_shares')
    reshared_by = db.relationship('User', foreign_keys=[reshared_by_id])

class UserFolderShare(db.Model):
    __tablename__ = 'user_folder_share'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)
    folder_id = db.Column(db.Integer, db.ForeignKey('folder.id', ondelete='CASCADE'), primary_key=True)
    reshared_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    can_download = db.Column(db.Boolean, default=False, nullable=False)
    can_reshare = db.Column(db.Boolean, default=False, nullable=False)
    can_copy = db.Column(db.Boolean, default=False, nullable=False)

    user = db.relationship('User', foreign_keys=[user_id], back_populates='folder_shares')
    folder = db.relationship('Folder', back_populates='user_shares')
    reshared_by = db.relationship('User', foreign_keys=[reshared_by_id])

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='user')
    plan_id = db.Column(db.Integer, db.ForeignKey('plan.id'))
    used_storage = db.Column(db.BigInteger, default=0)
    
    files = db.relationship('File', backref='user', lazy=True)
    folders = db.relationship('Folder', backref='user', lazy=True)
    subscriptions = db.relationship('Subscription', backref='user', lazy=True)
    payments = db.relationship('Payment', backref='user', lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True)

    file_shares = db.relationship('UserFileShare', foreign_keys=[UserFileShare.user_id], back_populates='user', cascade="all, delete-orphan")
    folder_shares = db.relationship('UserFolderShare', foreign_keys=[UserFolderShare.user_id], back_populates='user', cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_token(self, expires_sec=1800):
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        return s.dumps(self.id, salt='password-reset-salt')

    @staticmethod
    def verify_reset_token(token):
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, salt='password-reset-salt', max_age=1800)
        except:
            return None
        return User.query.get(user_id)

class Plan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    size_limit = db.Column(db.BigInteger, nullable=False) # in bytes
    price = db.Column(db.Float)
    duration = db.Column(db.Integer) # in days
    subscriptions = db.relationship('Subscription', backref='plan', lazy=True)

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    folder_id = db.Column(db.Integer, db.ForeignKey('folder.id'), nullable=True)
    filename = db.Column(db.String(255), nullable=False)
    path = db.Column(db.String(512), nullable=False, unique=True)
    size = db.Column(db.BigInteger, nullable=False)
    mime_type = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    encrypted_key = db.Column(db.String(255))
    thumbnail_path = db.Column(db.String(255))
    user_shares = db.relationship('UserFileShare', back_populates='file', cascade="all, delete-orphan")

class Folder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('folder.id'), nullable=True)
    name = db.Column(db.String(255), nullable=False)
    files = db.relationship('File', backref='folder', lazy='dynamic', cascade="all, delete-orphan")
    children = db.relationship('Folder', backref=db.backref('parent', remote_side=[id]), lazy='dynamic', cascade="all, delete-orphan")
    user_shares = db.relationship('UserFolderShare', back_populates='folder', cascade="all, delete-orphan")

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('plan.id'), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=False)
    active = db.Column(db.Boolean, default=True)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('plan.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    txn_id = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    link = db.Column(db.String(255))
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)