from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker, Session

SQLALCHEMY_DATABASE_URL = "sqlite:///./zclear.db"

# connect_args={"check_same_thread": False} is needed only for SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class SessionState(Base):
    __tablename__ = "session_state"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    status = Column(String, default="RECEIVED")  # 'RECEIVED', 'EXTRACTING', 'AUDITING', 'PENDING_REMEDY', 'COMPLETED', 'ERROR'
    raw_text = Column(Text, nullable=True)       # Store raw invoice text
    extracted_json = Column(Text, nullable=True) # Store extracted structured data
    audit_report = Column(Text, nullable=True)   # Store audit report
    progress = Column(Text, default="{}")        # Storing agent progress as JSON string

def update_session_status(db: Session, session_id: str, new_status: str):
    """
    Update the status of a specific session by its session_id.
    """
    session_record = db.query(SessionState).filter(SessionState.session_id == session_id).first()
    if session_record:
        session_record.status = new_status
        db.commit()
        db.refresh(session_record)
    return session_record
