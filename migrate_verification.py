from app import create_app, db
from sqlalchemy import text

def add_verification_columns():
    app = create_app()
    
    with app.app_context():
        try:
            # Add verification columns
            db.session.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS is_verified BOOLEAN DEFAULT FALSE,
                ADD COLUMN IF NOT EXISTS verification_token VARCHAR(100),
                ADD COLUMN IF NOT EXISTS token_expires_at TIMESTAMP;
            """))
            
            # Set existing users as verified
            db.session.execute(text("""
                UPDATE users SET is_verified = TRUE WHERE is_verified IS NULL;
            """))
            
            db.session.commit()
            print("Verification columns added successfully!")
            
        except Exception as e:
            print(f"Migration error: {e}")
            db.session.rollback()

if __name__ == '__main__':
    add_verification_columns()