"""
    Security and cypto utilities module.

    Includes funcions for password hashing with  
    bcrypt and generation tasks
"""


from passlib.context import CryptContext

from core.config import settings

# Sets up the Bcrypt algorithm for password encryption
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Takes a plain-text password and returns its hashed version."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compares a plain-text password against a stored hash."""
    return pwd_context.verify(plain_password, hashed_password)