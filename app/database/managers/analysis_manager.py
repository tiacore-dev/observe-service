import logging
import json
from app.database.models.analysis import AnalysisResult
from app.database.db_globals import Session
from app.utils.db_get import get_prompt_name


class AnalysisManager:
    def __init__(self):
        self.Session = Session

    def save_analysis_result(self, prompt_id, result_text, filters, tokens_input, tokens_output):
        session = self.Session()
        try:
            analysis_id = AnalysisResult().save(
                session=session,
                prompt_id=prompt_id,
                result_text=result_text,
                filters=filters,
                tokens_input=tokens_input,
                tokens_output=tokens_output
            )
            return analysis_id
        except Exception as e:
            logging.error(f"Ошибка при сохранении анализа: {e}")
            raise
        finally:
            session.close()

    def get_analysis_all(self, offset=0, limit=10):
        session = self.Session()
        try:
            analyses = (
                session.query(AnalysisResult)
                # Сортировка по времени
                .order_by(AnalysisResult.timestamp.desc())
                .offset(offset)
                .limit(limit)
                .all()
            )
            # Общее количество записей
            total_count = session.query(AnalysisResult).count()
            logging.info(f"""Найдено {total_count} анализов, возвращаем {
                         len(analyses)} начиная с {offset}""")
            result = [
                {
                    'analysis_id': analysis.analysis_id,
                    'prompt_id': analysis.prompt_id,
                    'prompt_name': get_prompt_name(analysis.prompt_id),
                    'filters': json.loads(analysis.filters) if analysis.filters else 'Не указаны',
                    'timestamp': analysis.timestamp.isoformat(),
                    'preview': analysis.result_text[:100] + '...' if len(analysis.result_text) > 100 else analysis.result_text
                }
                for analysis in analyses
            ]
            return {'analyses': result, 'total_count': total_count}
        except Exception as e:
            logging.error(f"Ошибка при получении анализов: {e}")
            return {'error': str(e), 'analyses': [], 'total_count': 0}
        finally:
            session.close()

    def get_analysis_by_id(self, analysis_id):
        session = self.Session()
        try:
            analysis = session.query(AnalysisResult).filter_by(
                analysis_id=analysis_id).first()
            if analysis:
                try:
                    # Десериализация фильтров
                    filters = json.loads(
                        analysis.filters) if analysis.filters else None
                except json.JSONDecodeError:
                    filters = "Некорректные данные"

                # Преобразование фильтров в читаемый формат
                filters_readable = (
                    ", ".join([f"{key}: {value}" for key, value in filters.items()]) if isinstance(
                        filters, dict) else filters
                )

                return {
                    'analysis_id': analysis.analysis_id,
                    'prompt_id': analysis.prompt_id,
                    # Название промпта
                    'prompt_name': get_prompt_name(analysis.prompt_id),
                    'timestamp': analysis.timestamp.isoformat(),
                    'result_text': analysis.result_text,
                    'filters': filters_readable or 'Не указаны',
                    'tokens_input': analysis.tokens_input or 'Неизвестно',
                    'tokens_output': analysis.tokens_output or 'Неизвестно'
                }
            return None
        except Exception as e:
            logging.error(f"Ошибка при получении анализа по ID: {e}")
            raise e
        finally:
            session.close()
