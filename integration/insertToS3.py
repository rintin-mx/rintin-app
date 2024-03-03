import boto3
import datetime
from config import aws_access_key_id, aws_secret_access_key
from urllib.parse import quote

def insertImage(image, seller_id, bucket_name):
    s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
    try:
        fecha_actual = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        rutaS3 = f'img/{seller_id}/{fecha_actual}'
        # La clave aquí es ExtraArgs={'ACL':'public-read'} para hacer el archivo público
        s3.upload_fileobj(image, bucket_name, rutaS3, ExtraArgs={'ACL':'public-read'})
        file_url = f'https://{bucket_name}.s3.us-east-2.amazonaws.com/{rutaS3}'
        return file_url
    except Exception as e:
        print(e)
        return False

def insertOrderImage(image, order_id, bucket_name):
    s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
    try:
        fecha_actual = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        rutaS3 = f'img/entregas/{order_id}/{fecha_actual}'
        # La clave aquí es ExtraArgs={'ACL':'public-read'} para hacer el archivo público
        s3.upload_fileobj(image, bucket_name, rutaS3, ExtraArgs={'ACL':'public-read'})
        file_url = f'https://{bucket_name}.s3.us-east-2.amazonaws.com/{rutaS3}'
        return file_url
    except Exception as e:
        print(e)
        return False