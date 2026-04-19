import json
import os
from datetime import datetime
from app.db.session import engine, Base, SessionLocal
from app.db.models import User, ModelRegistry
from app.core.security import get_password_hash

def init_db():
    # Create tables
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # 1. Seed Users if they don't exist
    users = [
        {"username": "lender_a", "tenant_id": "tenant_a"},
        {"username": "lender_b", "tenant_id": "tenant_b"}
    ]
    
    for u_data in users:
        user = db.query(User).filter(User.username == u_data["username"]).first()
        if not user:
            print(f"Seeding user: {u_data['username']}...")
            new_user = User(
                username=u_data["username"],
                hashed_password=get_password_hash("password123"),
                tenant_id=u_data["tenant_id"]
            )
            db.add(new_user)
    
    # 2. Seed Model Registry from existing JSON if present
    registry_path = "models/registry.json"
    if os.path.exists(registry_path):
        try:
            with open(registry_path, 'r') as f:
                data = json.load(f)
                
            existing = db.query(ModelRegistry).filter(ModelRegistry.version == data["version"]).first()
            if not existing:
                print(f"Importing model registry v{data['version']} to database...")
                entry = ModelRegistry(
                    version=data["version"],
                    trained_at=datetime.fromisoformat(data["trained_at"]),
                    metrics=data["metrics"],
                    feature_count=data["feature_count"]
                )
                db.add(entry)
        except Exception as e:
            print(f"Warning: Could not import registry.json: {e}")

    db.commit()
    db.close()
    print("Database initialization complete!")

if __name__ == "__main__":
    init_db()
