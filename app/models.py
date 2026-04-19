from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Float, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
import json

from app.database import Base

class Candidate(Base):
    __tablename__ = "candidates"

    # In Notion, IDs are UUIDs. Therefore, using String as primary key to preserve traceability.
    id = Column(String(50), primary_key=True, index=True)
    name_kr = Column(String(100))
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    
    raw_text = Column(Text, nullable=False)
    document_hash = Column(String(64), nullable=False)
    
    # 분산 트랜잭션 복구용 Sync Flags
    is_duplicate = Column(Integer, default=0)
    duplicate_of = Column(String(64), nullable=True)
    is_parsed = Column(Boolean, default=False)
    is_neo4j_synced = Column(Boolean, default=False)
    is_pinecone_synced = Column(Boolean, default=False)
    last_error = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    birth_year = Column(Integer, nullable=True)
    education_json = Column(Text, nullable=True)
    careers_json = Column(Text, nullable=True)

    # Relationship
    parsing_cache = relationship("ParsingCache", back_populates="candidate", uselist=False, cascade="all, delete-orphan")


class ParsingCache(Base):
    __tablename__ = "parsing_cache"

    candidate_id = Column(String(50), ForeignKey("candidates.id", ondelete="CASCADE"), primary_key=True)
    prompt_version = Column(String(20), nullable=False)
    logic_hash = Column(String(64), nullable=False, index=True)
    
    # SQLite does not have JSONB natively in all versions SQLAlchemy targets without specific dialects, 
    # so we use Text, but treat it as JSON in python logic.
    parsed_json = Column(Text, nullable=False)
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    candidate = relationship("Candidate", back_populates="parsing_cache")

    @property
    def parsed_dict(self):
        return json.loads(self.parsed_json) if self.parsed_json else {}

    @parsed_dict.setter
    def parsed_dict(self, value):
        self.parsed_json = json.dumps(value, ensure_ascii=False)
