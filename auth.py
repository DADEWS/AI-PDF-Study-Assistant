# Import password hashing tools
from passlib.context import CryptContext


# Create password hashing context
password_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


# Hash a plain password
def hash_password(password):
    return password_context.hash(password)


# Verify a plain password against a hashed password
def verify_password(password, hashed_password):
    return password_context.verify(
        password,
        hashed_password
    )