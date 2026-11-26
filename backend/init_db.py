from backend.database import Base, engine
from backend.models.user import User, Workspace

Base.metadata.create_all(bind=engine)

print("Database tables created successfully!")