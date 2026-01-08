from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
import sys

load_dotenv()

class Database:
    def __init__(self):
        self.db_url = None
        self.engine = None
        self.SessionLocal = None
        self._initialize()
    
    def _initialize(self):
        """Initialize database connection with error handling"""
        try:
            self.db_url = f"mysql+pymysql://{os.getenv('dbuser')}:{os.getenv('dbpassword')}@{os.getenv('dbhost')}:{os.getenv('dbport')}/{os.getenv('dbname')}"
            self.engine = create_engine(self.db_url, pool_pre_ping=True)
            self.SessionLocal = sessionmaker(bind=self.engine, autocommit=False, autoflush=False)
            
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            print(" Database connection established")
            self._create_tables()
            
        except Exception as e:
            print(f" Database connection failed: {e}")
            print(" Running in fallback mode")
            self.SessionLocal = sessionmaker()
    
    def _create_tables(self):
        """Create ALL necessary tables"""
        try:
            with self.engine.begin() as conn:
                print("🔄 Creating database tables...")
                
                # users table 
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        email VARCHAR(255) UNIQUE NOT NULL,
                        username VARCHAR(100) UNIQUE NOT NULL,
                        password_hash VARCHAR(255) NOT NULL,
                        full_name VARCHAR(255),
                        is_active BOOLEAN DEFAULT TRUE,
                        is_verified BOOLEAN DEFAULT FALSE,
                        failed_login_attempts INT DEFAULT 0,
                        locked_until TIMESTAMP NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        INDEX idx_email (email),
                        INDEX idx_username (username),
                        INDEX idx_is_active (is_active)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """))
                print("    ✅ Users table created")
                
                # password reset tokens table 
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS password_reset_tokens (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id INT NOT NULL,
                        token VARCHAR(64) UNIQUE NOT NULL,
                        expires_at DATETIME NOT NULL,
                        used BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                        INDEX idx_token (token),
                        INDEX idx_user_id (user_id),
                        INDEX idx_expires_at (expires_at)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """))
                print("    ✅ Password reset tokens table created")
                
                # conversations table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS conversations (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        session_id VARCHAR(100) NOT NULL UNIQUE,
                        user_id INT NULL,
                        title VARCHAR(200) DEFAULT 'New Conversation',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
                        INDEX idx_session_id (session_id),
                        INDEX idx_user_id (user_id),
                        INDEX idx_updated_at (updated_at)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """))
                print("    ✅ Conversations table created")
                
                # messages table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS messages (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        conversation_id INT NOT NULL,
                        role VARCHAR(20) NOT NULL,
                        content TEXT NOT NULL,
                        citations JSON,
                        metadata JSON,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
                        INDEX idx_conversation_id (conversation_id),
                        INDEX idx_created_at (created_at)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """))
                print("    ✅ Messages table created")
                
                # Rate limit logs table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS rate_limit_logs (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        ip_address VARCHAR(45) NOT NULL,
                        endpoint VARCHAR(100) NOT NULL,
                        request_count INT DEFAULT 1,
                        window_start TIMESTAMP NOT NULL,
                        window_end TIMESTAMP NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        INDEX idx_ip_endpoint (ip_address, endpoint),
                        INDEX idx_window (window_start, window_end)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """))
                print("    ✅ Rate limit logs table created")
                
                # System logs table 
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS system_logs (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        level VARCHAR(20) NOT NULL,
                        service VARCHAR(50) NOT NULL,
                        message TEXT NOT NULL,
                        details JSON,
                        ip_address VARCHAR(45),
                        user_id INT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        INDEX idx_level (level),
                        INDEX idx_service (service),
                        INDEX idx_created_at (created_at),
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """))
                print(" System logs table created")
                
                print("All database tables created successfully!")
                
        except Exception as e:
            print(f" Table creation error: {e}")
            import traceback
            traceback.print_exc()
    
    def get_session(self):
        """Get database session with context manager"""
        return self.SessionLocal()
    
    def close(self):
        """Close database connection"""
        if self.engine:
            self.engine.dispose()
            print(" Database connection closed")

# Global database instance
db_manager = Database()


def get_db():
    """
    FastAPI dependency that yields a database session.
    Usage: db: Session = Depends(get_db)
    """
    session = db_manager.get_session()
    try:
        yield session
    finally:
        session.close()

if __name__ == "__main__":
    print(" Testing database...")
    try:
        with db_manager.engine.connect() as conn:
            tables = conn.execute(text("SHOW TABLES")).fetchall()
            print(f" Found {len(tables)} tables:")
            for table in tables:
                print(f"  - {table[0]}")
    except Exception as e:
        print(f" Test failed: {e}")
    db_manager.close()