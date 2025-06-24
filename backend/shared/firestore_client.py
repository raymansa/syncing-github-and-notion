from typing import Optional
from werkzeug.security import generate_password_hash, check_password_hash
from google.cloud import firestore

from .data_models import User

class FirestoreClient:
    def __init__(self):
        # The client library will automatically find the project's
        # credentials when running on GCP.
        self.db = firestore.Client()
        self.users_collection = self.db.collection('users')

    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Retrieves a user document from Firestore by their email address.
        Returns a User object or None if not found.
        """
        query = self.users_collection.where("email", "==", email).limit(1)
        results = list(query.stream())

        if not results:
            return None
        
        user_doc = results[0]
        user_data = user_doc.to_dict()
        
        return User(
            id=user_doc.id,
            email=user_data.get("email"),
            password_hash=user_data.get("password_hash")
        )

    def create_user(self, email: str, password: str) -> User:
        """
        Creates a new user in Firestore with a hashed password.
        Returns the newly created User object.
        """
        # Check if user already exists
        if self.get_user_by_email(email):
            raise ValueError(f"User with email {email} already exists.")

        # Securely hash the password before storing
        password_hash = generate_password_hash(password)
        
        user_data = {
            "email": email,
            "password_hash": password_hash
        }

        # Add a new document with an auto-generated ID
        doc_ref = self.users_collection.add(user_data)[1]
        
        return User(
            id=doc_ref.id,
            email=email,
            password_hash=password_hash
        )

    def verify_password(self, password_hash: str, password_to_check: str) -> bool:
        """Verifies a password against its stored hash."""
        return check_password_hash(password_hash, password_to_check)