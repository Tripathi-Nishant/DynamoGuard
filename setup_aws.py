import boto3
import time

dynamodb = boto3.resource('dynamodb')

def create_table():
    table_name = 'Exam_UserTraffic'
    try:
        print(f"Creating table {table_name}...")
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {'AttributeName': 'user_id', 'KeyType': 'HASH'},
                {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'user_id', 'AttributeType': 'S'},
                {'AttributeName': 'timestamp', 'AttributeType': 'N'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
        print(f"Table {table_name} created successfully!")
    except Exception as e:
        print(f"Table might already exist: {e}")

if __name__ == '__main__':
    create_table()
