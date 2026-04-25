from sqlalchemy import create_engine, Column, Integer, String, Text
import sqlalchemy.types as types
from sqlalchemy.orm import declarative_base, sessionmaker, Session

class VectorType(types.UserDefinedType):
    def __init__(self, dim):
        self.dim = dim
        
    def get_col_spec(self):
        return f"VECTOR({self.dim})"

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
    status = Column(String, default="RECEIVED")  # 'RECEIVED', 'EXTRACTING', 'AUDITING', 'PENDING_REMEDY', 'COMPLETED'
    raw_text = Column(Text, nullable=True)       # Store raw invoice text
    extracted_json = Column(Text, nullable=True) # Store extracted structured data
    audit_report = Column(Text, nullable=True)   # Store audit report
    progress = Column(Text, default="{}")        # Storing agent progress as JSON string
    error_log = Column(Text, nullable=True)      # Store error logs

class ComplianceRegulation(Base):
    __tablename__ = "compliance_regulation"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    content = Column(Text)
    hs_code = Column(String(50), index=True)
    applicable_country = Column(String(100), index=True)
    vector_data = Column(VectorType(2048))  # For embedding-3 models which have 2048 dimensions or 1536


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
