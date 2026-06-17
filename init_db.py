import os

# 1. Purga absoluta de variables AWS y configuraciones de Proxy en la memoria del script
for key in list(os.environ.keys()):
    if key.startswith("AWS_") or "PROXY" in key.upper():
        os.environ.pop(key, None)

# Forzamos a que ignore cualquier proxy para el tráfico local
os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""
os.environ["NO_PROXY"] = "127.0.0.1,localhost"

import boto3
from botocore.config import Config

print("Conectando a DynamoDB Local (Aislamiento de Red Activo)...")

# 2. Creamos una sesión limpia e independiente de los archivos del sistema (~/.aws/)
# Usamos strings genéricos largos que simulen el formato exacto que espera el validador nativo
session = boto3.Session(
    aws_access_key_id='DUMMYIDEXAMPLEKEYS',
    aws_secret_access_key='DUMMYBOPTIONSAMPLESECRETKEY',
    aws_session_token=None,  # Bloqueamos explícitamente cualquier token de sesión
    region_name='us-east-1'
)

# 3. Conectamos usando 127.0.0.1 para evitar enredos con la resolución IPv6 de Windows
dynamodb = session.client(
    'dynamodb',
    endpoint_url='http://127.0.0.1:8000',
    config=Config(signature_version='v4')
)

try:
    response = dynamodb.create_table(
        TableName='SmartStopTable',
        AttributeDefinitions=[
            {'AttributeName': 'PK', 'AttributeType': 'S'},
            {'AttributeName': 'CO', 'AttributeType': 'S'},
            {'AttributeName': 'GSI1_Correo', 'AttributeType': 'S'}
        ],
        KeySchema=[
            {'AttributeName': 'PK', 'KeyType': 'HASH'},
            {'AttributeName': 'CO', 'KeyType': 'RANGE'}
        ],
        BillingMode='PAY_PER_REQUEST',
        GlobalSecondaryIndexes=[
            {
                'IndexName': 'GSI1-Correo-Index',
                'KeySchema': [
                    {'AttributeName': 'GSI1_Correo', 'KeyType': 'HASH'}
                ],
                'Projection': {
                    'ProjectionType': 'ALL'
                }
            }
        ]
    )
    print("\n¡Por fin! La Tabla Única 'SmartStopTable' ha sido creada con éxito en Docker.")
except Exception as e:
    print(f"\nError al intentar crear la tabla: {e}")