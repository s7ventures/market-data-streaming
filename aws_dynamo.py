import os
from tinydb import TinyDB, Query
import boto3
from botocore.exceptions import ClientError

class MarketDataStore:
    def __init__(self, db_path='market_data.json', table_name='market_data'):
        self.backend = os.getenv('STORAGE_BACKEND', 'tinydb')
        self.table_name = table_name
        if self.backend == 'dynamo':
            self.dynamo_client = boto3.resource('dynamodb')
            self.table = self.dynamo_client.Table(self.table_name)
        else:
            self.db_path = db_path
            self.db = TinyDB(self.db_path)

    def create_table(self):
        if self.backend == 'dynamo':
            try:
                self.dynamo_client.create_table(
                    TableName=self.table_name,
                    KeySchema=[
                        {'AttributeName': 'symbol', 'KeyType': 'HASH'},
                        {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}
                    ],
                    AttributeDefinitions=[
                        {'AttributeName': 'symbol', 'AttributeType': 'S'},
                        {'AttributeName': 'timestamp', 'AttributeType': 'S'}
                    ],
                    ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
                )
                self.table.wait_until_exists()
            except ClientError as e:
                if e.response['Error']['Code'] != 'ResourceInUseException':
                    raise
        else:
            if not os.path.exists(self.db_path):
                with open(self.db_path, 'w') as f:
                    f.write('')  # Create an empty file if it doesn't exist

    def batch_write(self, items):
        if self.backend == 'dynamo':
            with self.table.batch_writer() as batch:
                for item in items:
                    batch.put_item(Item=item)
        else:
            query = Query()
            for item in items:
                if not self.db.search((query.symbol == item['symbol']) & (query.timestamp == item['timestamp'])):
                    self.db.insert(item)
