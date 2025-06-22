import secrets
import string

def generate_secret_key(length=50):
    """Generate a secure secret key for Django"""
    chars = string.ascii_letters + string.digits + '!@#$%^&*(-_=+)'
    return ''.join(secrets.choice(chars) for _ in range(length))

if __name__ == "__main__":
    key = generate_secret_key()
    print(f"SECRET_KEY={key}")
    print(f"\nAdd this line to your .env file in the backend directory:")
    print(f"SECRET_KEY={key}") 