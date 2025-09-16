from models import db

def create_database(app):
    with app.app_context():
        db.drop_all()
        db.create_all()
