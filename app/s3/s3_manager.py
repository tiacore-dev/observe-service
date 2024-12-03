import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
import logging





class S3Manager:
    def __init__(self, endpoint_url, region_name, aws_access_key_id, aws_secret_access_key):
        logging.info("Инициализация S3 клиента.")
        self.s3 = boto3.client(
            's3',
            endpoint_url=endpoint_url,
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            config=Config(s3={'addressing_style': 'path'})
        )

    def upload_file(self, file_content, bucket_name, object_name):
        """
        Загружает содержимое файла в S3.
        
        :param file_content: Данные файла в формате байтов.
        :param bucket_name: Название S3-бакета.
        :param object_name: Имя объекта в S3.
        """
        logging.info(f"Загрузка файла в bucket '{bucket_name}' с именем 'telegram_docs/{object_name}'.")
        try:
            # Используем upload_fileobj для загрузки данных из памяти
            self.s3.upload_fileobj(file_content, bucket_name, f"telegram_docs/{object_name}")
            logging.info(f"Файл успешно загружен в {bucket_name}/telegram_docs/{object_name}.")
        except ClientError as e:
            logging.error(f"Ошибка при загрузке файла: {e}")
            raise

    def upload_fileobj(self, file_obj, bucket_name, object_name):
        """Загружает файл напрямую из объекта файла в S3."""
        logging.info(f"Загрузка файла в bucket '{bucket_name}' с именем '{object_name}'.")
        try:
            self.s3.upload_fileobj(file_obj, bucket_name, "telegram_docs/"+object_name)
            logging.info(f"Файл успешно загружен в {bucket_name}/{object_name}.")
        except ClientError as e:
            logging.error(f"Ошибка при загрузке файла: {e}")

    def download_file(self, bucket_name, object_name, file_name):
        if file_name is None:
            file_name = object_name
        logging.info(f"Скачивание файла '{object_name}' из bucket '{bucket_name}' в '{file_name}'.")
        try:
            self.s3.download_file(bucket_name, object_name, "telegram_docs/"+file_name)
            logging.info(f"Файл '{object_name}' успешно скачан в '{file_name}'.")
        except ClientError as e:
            logging.error(f"Ошибка при скачивании файла '{object_name}': {e}")

    def list_files(self, bucket_name, prefix=""):
        logging.info(f"Получение списка файлов из bucket '{bucket_name}' с префиксом '{prefix}'.")
        try:
            response = self.s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
            files = [obj['Key'] for obj in response.get('Contents', [])]
            logging.info(f"Найдено {len(files)} файлов.")
            return files
        except ClientError as e:
            logging.error(f"Ошибка при получении списка файлов из bucket '{bucket_name}': {e}")
            return []

    def delete_file(self, bucket_name, object_name):
        logging.info(f"Удаление файла '{object_name}' из bucket '{bucket_name}'.")
        try:
            self.s3.delete_object(Bucket=bucket_name, Key="telegram_docs/"+object_name)
            logging.info(f"Файл '{object_name}' успешно удален из bucket '{bucket_name}'.")
        except ClientError as e:
            logging.error(f"Ошибка при удалении файла '{object_name}': {e}")



    def file_exists(self, bucket_name, object_name):
        logging.info(f"Проверка существования файла '{object_name}' в bucket '{bucket_name}'.")
        try:
            self.s3.head_object(Bucket=bucket_name, Key="telegram_docs/"+object_name)
            logging.info(f"Файл '{object_name}' существует в bucket '{bucket_name}'.")
            return True
        except ClientError as e:
            logging.warning(f"Файл '{object_name}' не найден в bucket '{bucket_name}': {e}")
            return False

    def get_file_metadata(self, bucket_name, object_name):
        logging.info(f"Получение метаданных для файла '{object_name}' из bucket '{bucket_name}'.")
        try:
            response = self.s3.head_object(Bucket=bucket_name, Key="telegram_docs/"+object_name)
            logging.info(f"Метаданные для файла '{object_name}' получены.")
            return {
                'ContentType': response['ContentType'],
                'ContentLength': response['ContentLength'],
                'LastModified': response['LastModified'],
            }
        except ClientError as e:
            logging.error(f"Ошибка при получении метаданных для файла '{object_name}': {e}")
            return None

    def get_file(self, bucket_name, object_name):
        logging.info(f"Получение файла '{object_name}' из bucket '{bucket_name}'.")
        try:
            response = self.s3.get_object(Bucket=bucket_name, Key="telegram_docs/"+object_name)
            file_content = response['Body'].read()  # Чтение содержимого файла в байты
            logging.info(f"Файл '{object_name}' успешно получен.")
            return file_content
        except ClientError as e:
            logging.error(f"Ошибка при получении файла '{object_name}': {e}")
            return None