from app import create_app, db

app = create_app()

def init_database():
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("Database initialization complete.")

if __name__ == '__main__':
    init_database()
