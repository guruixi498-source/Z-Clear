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
    status = Column(String, default="RECEIVED")  # 'RECEIVED', 'EXTRACTING', 'AUDITING', 'PENDING_REMEDY', 'COMPLETED'
    raw_text = Column(Text, nullable=True)       # Store raw invoice text
    extracted_json = Column(Text, nullable=True) # Store extracted structured data
    audit_report = Column(Text, nullable=True)   # Store audit report
    progress = Column(Text, default="{}")        # Storing agent progress as JSON string
    regulation_context = Column(Text, nullable=True) # Store retrieved regulations
    error_log = Column(Text, nullable=True)      # Store error messages

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

from datetime import datetime

class ComplianceRegulation(Base):
    __tablename__ = "compliance_regulations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255))
    content = Column(Text)
    hs_code = Column(String(50), index=True, nullable=True)
    country = Column(String(100), index=True)
    embedding = Column(Text)  # stored as JSON string in sqlite, or vector in mariadb
    create_time = Column(Text, default=lambda: datetime.utcnow().isoformat())
    update_time = Column(Text, default=lambda: datetime.utcnow().isoformat(), onupdate=lambda: datetime.utcnow().isoformat())

def insert_regulation(db: Session, title: str, content: str, country: str, embedding: list[float], hs_code: str = None):
    import json
    db_reg = ComplianceRegulation(
        title=title,
        content=content,
        country=country,
        hs_code=hs_code,
        embedding=json.dumps(embedding)
    )
    db.add(db_reg)
    db.commit()
    db.refresh(db_reg)
    return db_reg

def search_similar_regulations(db: Session, query_embedding: list[float], top_k: int = 3, hs_code: str = None):
    import json
    from sqlalchemy import text
    
    vec_str = json.dumps(query_embedding)
    
    try:
        # 尝试 MariaDB Vector 引擎原生语法 (VEC_DISTANCE_COSINE)
        sql = "SELECT id, title, content, hs_code, country FROM compliance_regulations "
        params = {"vec": vec_str, "top_k": top_k}
        
        if hs_code:
            sql += " WHERE hs_code = :hs_code "
            params["hs_code"] = hs_code
            
        sql += " ORDER BY VEC_DISTANCE_COSINE(embedding, VEC_FromText(:vec)) LIMIT :top_k"
        
        result = db.execute(text(sql), params).fetchall()
        return [dict(row._mapping) for row in result]
    except Exception as e:
        # SQLite 测试环境降级方案 (Fallback)
        query = db.query(ComplianceRegulation)
        if hs_code:
            query = query.filter(ComplianceRegulation.hs_code == hs_code)
        
        results = query.limit(top_k).all()
        return [
            {
                "id": r.id, 
                "title": r.title, 
                "content": r.content, 
                "hs_code": r.hs_code, 
                "country": r.country
            } for r in results
        ]

def get_regulation_by_hs_code(db: Session, hs_code: str):
    return db.query(ComplianceRegulation).filter(ComplianceRegulation.hs_code == hs_code).all()
