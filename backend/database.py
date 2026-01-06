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
            
            print("✅ Database connection established")
            self._create_tables()
            
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            print("⚠️ Running in fallback mode (conversations won't be saved)")
            # Create a dummy session for fallback
            self.SessionLocal = sessionmaker()
    
    def _create_tables(self):
        """Create necessary tables if they don't exist"""
        try:
            with self.engine.begin() as conn:
                # Conversations table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS conversations_table (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        session_id VARCHAR(100) NOT NULL UNIQUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        INDEX idx_session_id (session_id)
                    )
                """))
                
                # Messages table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS messages_table (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        conversation_id INT NOT NULL,
                        role VARCHAR(20) NOT NULL,
                        text TEXT NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        citations JSON,
                        route VARCHAR(50),
                        refusal BOOLEAN DEFAULT FALSE,
                        FOREIGN KEY (conversation_id) 
                            REFERENCES conversations_table(id) 
                            ON DELETE CASCADE,
                        INDEX idx_conversation_id (conversation_id),
                        INDEX idx_timestamp (timestamp)
                    )
                """))
                
                #  System logs table for ingest tracking
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS system_logs (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        action VARCHAR(50),
                        details JSON,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        INDEX idx_action (action),
                        INDEX idx_timestamp (timestamp)
                    )
                """))
                
            print("✅ Database tables verified/created")
            
        except Exception as e:
            print(f"⚠️ Table creation error (might already exist): {e}")
    
    def get_session(self):
        """Get database session with context manager"""
        return self.SessionLocal()
    
    def close(self):
        """Close database connection"""
        if self.engine:
            self.engine.dispose()
            print("✅ Database connection closed")

# Global database instance
db_manager = Database()

# Convenience function for FastAPI dependency injection
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
