from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import SQLAlchemyError

# ====================== DATABASE SETUP ======================
Base = declarative_base()

class MessageHistory(Base):
    __tablename__ = 'message_history'
    id = Column(Integer, primary_key=True)
    command = Column(Text)
    generated_message = Column(Text)
    recipient = Column(String(100))
    category = Column(String(50))
    sent_at = Column(DateTime, default=datetime.now)
    status = Column(String(20), default='pending')

class UserSettings(Base):
    __tablename__ = 'user_settings'
    id = Column(Integer, primary_key=True)
    default_delay = Column(Float, default=1.0)
    retry_count = Column(Integer, default=3)
    theme = Column(String(20), default='light')

class CustomTemplates(Base):
    __tablename__ = 'custom_templates'
    id = Column(Integer, primary_key=True)
    category = Column(String(50))
    template_text = Column(Text)
    created_at = Column(DateTime, default=datetime.now)

# Initialize database
engine = create_engine('sqlite:///whatsapp_agent.db')
Session = sessionmaker(bind=engine)

def initialize_database():
    Base.metadata.create_all(engine)
    session = Session()
    
    if not session.query(UserSettings).first():
        session.add(UserSettings())
    
    if not session.query(CustomTemplates).first():
        session.add_all([
            CustomTemplates(category='love', template_text="Hey {name}, thinking of you today ❤️"),
            CustomTemplates(category='apology', template_text="Hi {name}, I owe you an apology...")
        ])
    
    session.commit()
    session.close()

initialize_database()