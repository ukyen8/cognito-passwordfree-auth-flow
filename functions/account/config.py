# Standard library
import os


class Configuration:
    def __init__(self) -> None:
        self.account_table_name: str = os.environ["ACCOUNT_TABLE_NAME"]
        self.region_name: str = os.environ["REGION_NAME"]
        self.app_client_id: str = os.environ["APP_CLIENT_ID"]
