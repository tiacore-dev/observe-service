import json
from sqlalchemy import Column, String, Text, DateTime, Integer
from datetime import datetime
from app.database.db_setup import Base
import uuid

class AnalysisResult(Base):
    __tablename__ = 'analysis_results'

    analysis_id = Column(String, primary_key=True)
    prompt_id = Column(String, nullable=False)  # Привязка к таблице промптов
    result_text = Column(Text, nullable=False)  # Результат анализа
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)  # Дата создания анализа
    filters = Column(String)  # Храним сериализованные фильтры
    tokens = Column(Integer)

    def save(self, session, prompt_id, result_text, filters, tokens):
        """
        Сохранение анализа.
        """
        try:
            serialized_filters = json.dumps(filters) if filters else None
            analysis_result = AnalysisResult(
                analysis_id=str(uuid.uuid4()),
                prompt_id=prompt_id,
                result_text=result_text,
                timestamp=datetime.utcnow(),
                filters=serialized_filters,
                tokens=tokens,
            )
            session.add(analysis_result)
            session.commit()
            return analysis_result.analysis_id
        except Exception as e:
            session.rollback()
            raise e
