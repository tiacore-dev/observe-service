from sqlalchemy import exists
from app.database.models.prompt import Prompt
import uuid
from app.database.db_globals import Session
import logging


class PromptManager:
    def __init__(self):
        self.Session = Session

    def add_prompt(self, prompt_name, text, use_automatic=False):
        session = self.Session()
        logging.info("Сохранение промпта в базу данных.")
        prompt_id = str(uuid.uuid4())
        new_prompt = Prompt(prompt_id=prompt_id, prompt_name=prompt_name, text=text, use_automatic=use_automatic)
        session.add(new_prompt)
        session.commit()
        session.close()
        logging.info("Промпт успешно сохранен.")
        return prompt_id

    def get_prompts(self):
        session = self.Session()
        try:
            logging.info(f"Получение промптов")
            prompts = session.query(Prompt).all()
            result = [[p.prompt_name, p.text, p.prompt_id, p.use_automatic] for p in prompts]
        finally:
            session.close()
        return result
    
    def get_prompt_by_prompt_id(self,  prompt_id):
        session = self.Session()
        try:
            logging.info(f"Получение промпта по prompt_id: {prompt_id}")
            prompt = session.query(Prompt).filter_by( prompt_id=prompt_id).first()
        finally:
            session.close()
        return prompt.to_dict()

    def get_prompt_by_prompt_name(self, prompt_name):
        session = self.Session()
        try:
            logging.info(f"Получение промпта по prompt_id: {prompt_name}")
            prompt = session.query(Prompt).filter_by(prompt_name=prompt_name).first()
            return prompt.to_dict()
        finally:
            session.close()
        

    def edit_prompt(self, prompt_id, new_text, new_prompt_name):
        session = self.Session()
        try:
            logging.info(f"Редактирование промпта '{prompt_id}'")
            prompt = session.query(Prompt).filter_by(prompt_id=prompt_id).first()
            if prompt:
                prompt.text = new_text
                prompt.prompt_name = new_prompt_name  # Обновляем имя промпта
                session.commit()
                logging.info(f"Промпт '{prompt_id}' обновлен ")
                return True  # Успешное редактирование
            else:
                logging.warning(f"Промпт '{prompt_id}' не найден")
                return False  # Промпт не найден
        except Exception as e:
            logging.error(f"Ошибка при редактировании промпта: {e}")
            session.rollback()
            raise e
        finally:
            session.close()



    def delete_prompt(self, prompt_id):
        session = self.Session()
        try:
            logging.info(f"Удаление промпта '{prompt_id}'")
            prompt = session.query(Prompt).filter_by(prompt_id=prompt_id).first()
            if prompt:
                session.delete(prompt)
                session.commit()
                logging.info(f"Промпт '{prompt_id}' успешно удален.")
            else:
                logging.warning(f"Промпт '{prompt_id}' не найден")
        except Exception as e:
            logging.error(f"Ошибка при удалении промпта: {e}")
            session.rollback()
            raise e
        finally:
            session.close()


    def get_automatic_prompt(self):
        session = self.Session()
        try:
            logging.info(f"Поиск автоматического промпта")
            prompt = session.query(Prompt).filter_by(use_automatic=True).first()  # Получаем первый промпт с флагом use_automatic=True
            
            # Возвращаем всю информацию о промпте, если он найден
            if prompt:
                logging.info(f"Автоматический промпт '{prompt.prompt_name}' найден")
                return prompt.to_dict()
            else:
                logging.info(f"Автоматический промпт не найден")
                return None
        except Exception as e:
            logging.error(f"Ошибка при поиске автоматического промпта: {e}")
            raise e
        finally:
            session.close()

        

    def reset_automatic_flag(self):
        logging.info(f"Сброс флага 'use_automatic' для всех промптов")
        session = self.Session()
        try:
            prompts = session.query(Prompt).filter_by(use_automatic=True).all()
            for prompt in prompts:
                prompt.use_automatic = False
            session.commit() 
            logging.info(f"Флаг 'use_automatic' сброшен для промптов.")
        except Exception as e:
            logging.error(f"Ошибка при сбросе флага 'use_automatic': {e}")
            session.rollback()
            raise e
        finally:
            session.close()


    def set_automatic_flag(self, prompt_id, use_automatic):
        logging.info(f"Установка флага 'use_automatic' для промпта ID: {prompt_id} на {use_automatic}.")
        session = self.Session()
        try:
            prompt = session.query(Prompt).filter_by(prompt_id=prompt_id).first()
            if prompt:
                prompt.use_automatic = use_automatic
                session.commit()
                logging.info(f"Флаг 'use_automatic' для промпта ID: {prompt_id} успешно обновлён на {use_automatic}.")
            else:
                logging.warning(f"Промпт ID: {prompt_id} не найден.")
                raise ValueError(f"Prompt with ID {prompt_id} not found")
        except Exception as e:
            logging.error(f"Ошибка при установке флага 'use_automatic' для промпта ID: {prompt_id}: {e}")
            session.rollback()
            raise e
        finally:
            session.close()
            logging.info(f"Сессия для установки флага 'use_automatic' для промпта ID: {prompt_id} закрыта.")


    def get_all_prompts(self):
        session = self.Session()
        try:
            logging.info(f"Получение промптов")
            prompts = session.query(Prompt).all()
            return prompts
        finally:
            session.close()