import json
from datetime import datetime

import boto3
from botocore.exceptions import NoCredentialsError

import example_utils

from hyperliquid.utils import constants


class S3:
    def __init__(self, aws_access_key_id, aws_secret_access_key):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )

    def save_json_to_s3(self, json_data, bucket_name, s3_file_path):
        try:
            json_string = json.dumps(json_data)

            # Загружаем JSON строку в S3
            self.s3_client.put_object(
                Bucket=bucket_name,
                Key=s3_file_path,
                Body=json_string,
                ContentType='application/json'
            )
            print(f"JSON данные успешно сохранены в {bucket_name}/{s3_file_path}")
            return True
        except NoCredentialsError:
            print("Учетные данные AWS не предоставлены или неверны")
            return False
        except Exception as e:
            print(f"Произошла ошибка при сохранении JSON: {e}")
            return False


class LP(S3):
    def __init__(self, aws_access_key_id, aws_secret_access_key, coin):

        super().__init__(aws_access_key_id, aws_secret_access_key)
        self.address, self.info, _ = example_utils.setup(constants.MAINNET_API_URL)
        self.coin = coin

        self.batch = []
        self.batch_size = 100
        self.idx = 1

    def subscribe(self):
        self.info.subscribe({"type": "l2Book", "coin": self.coin}, self.save_result)

    def save_result(self, response: str):
        if self.idx < self.batch_size:
            self.batch.append(response)
            self.idx += 1
        else:
            self.save_json_to_s3(json_data=self.batch,
                                 bucket_name='pvv-crypto-storage',
                                 s3_file_path=f'data/{datetime.now().strftime("%Y%m%d")}/{self.coin.replace("/","")}_{datetime.now().strftime("%Y%m%d%H%M%S%f")}.json')
            self.batch = []
            self.idx = 1


if __name__ == "__main__":
    # main()
    lp = LP(aws_access_key_id='AKIAQD6N3F7C4UGGJS2O',
            aws_secret_access_key='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',
            coin="UETH/USDC")
    lp.subscribe()
