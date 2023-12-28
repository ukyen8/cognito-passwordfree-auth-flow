# Standard library
import random
import uuid
from dataclasses import dataclass
from datetime import datetime

# Third-party
import boto3
from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler.exceptions import BadRequestError
from botocore.exceptions import ClientError
from mypy_boto3_cognito_idp import CognitoIdentityProviderClient
from mypy_boto3_dynamodb.service_resource import Table

# First-party
from functions.account.config import Configuration
from functions.account.models import Account, PatchAccount, PostAccount

logger = Logger()


@dataclass
class AccountManager:
    dynamodb_table: Table
    cognito_client: CognitoIdentityProviderClient
    config: Configuration
    logger: Logger

    def create_account(self, payload: PostAccount) -> uuid.UUID:
        try:
            response = self.cognito_client.sign_up(
                ClientId=self.config.app_client_id,
                Username=payload.email_address,
                Password="".join(
                    random.choice("1234567890") for _ in range(8)
                ),
                UserAttributes=[
                    {
                        "Name": "name",
                        "Value": f"{payload.first_name} {payload.last_name}",
                    },
                ],
            )
        except ClientError as exc:
            logger.exception(exc)
            raise BadRequestError("User already exists") from exc
        else:
            new_account = Account(
                account_id=uuid.UUID(response["UserSub"]),
                **payload.model_dump(),
            )
            self.dynamodb_table.put_item(
                Item=new_account.model_dump(mode="json", by_alias=True)
            )
            return new_account.id

    def get_account(self, account_id: str) -> Account | None:
        response = self.dynamodb_table.get_item(Key={"account_id": account_id})
        if response:
            return Account(**response["Item"])

    def patch_account(self, payload: PatchAccount) -> None:
        response = self.dynamodb_table.get_item(
            Key={"account_id": str(payload.id)}
        )
        if "Item" not in response:
            raise BadRequestError(
                "Account doesn't exist, cannot update details"
            )
        payload.modified_at = datetime.utcnow()
        attribute_updates = {
            key: {"Value": value, "Action": "PUT"}
            for key, value in payload.model_dump(
                mode="json", exclude={"id"}
            ).items()
        }

        self.dynamodb_table.update_item(
            Key={"account_id": str(payload.id)},
            AttributeUpdates=attribute_updates,
        )


def get_account_manager() -> AccountManager:
    _config = Configuration()
    _dynamodb_resource = boto3.resource("dynamodb", _config.region_name)
    _dynamodb_table: Table = _dynamodb_resource.Table(
        _config.account_table_name
    )
    _cognito_client: CognitoIdentityProviderClient = boto3.client(
        "cognito-idp", _config.region_name
    )

    return AccountManager(_dynamodb_table, _cognito_client, _config, logger)
