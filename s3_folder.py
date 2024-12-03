import boto3
from botocore.client import Config
import os
from dotenv import load_dotenv

load_dotenv()

endpoint_url = os.getenv('ENDPOINT_URL')
region_name = os.getenv('REGION_NAME')
aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
BUCKET_NAME = os.getenv('BUCKET_NAME')

s3 = boto3.client(
            's3',
            endpoint_url=endpoint_url,
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )



def create_folder(bucket_name, folder_name):
    # Добавление объекта с "/" в конце имени создаёт "папку"
    if not folder_name.endswith('/'):
        folder_name += '/'
    s3.put_object(Bucket=bucket_name, Key=folder_name)
    print(f"Папка {folder_name} успешно создана в бакете {bucket_name}")

def delete_folder(bucket_name, folder_name):
    # Убедитесь, что имя "папки" заканчивается на '/'
    if not folder_name.endswith('/'):
        folder_name += '/'
    
    # Получение всех объектов внутри "папки"
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_name)
    if 'Contents' in response:
        # Удаление объектов
        for obj in response['Contents']:
            s3.delete_object(Bucket=bucket_name, Key=obj['Key'])
            print(f"Удалён объект: {obj['Key']}")
        print(f"Папка {folder_name} успешно удалена из бакета {bucket_name}")
    else:
        print(f"Папка {folder_name} пуста или не существует.")


# Пример использования
delete_folder(BUCKET_NAME, "tekegram_docs")

# Пример использования
#create_folder(BUCKET_NAME, "telegram_docs")
