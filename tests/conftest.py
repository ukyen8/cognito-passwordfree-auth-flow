# Standard library
import unittest.mock
from dataclasses import dataclass
from typing import Callable

# Third-party
import boto3
import moto
import pytest
from aws_lambda_powertools import Logger
from mypy_boto3_cognito_idp import CognitoIdentityProviderClient
from mypy_boto3_dynamodb.service_resource import Table

# First-party
from functions.account.account_manager import AccountManager
from functions.account.config import Configuration
from functions.account.models import PostAccount


@pytest.fixture()
def account_table_name() -> str:
    return "AccountManagementTable"


@pytest.fixture()
def mocked_configuration(
    account_table_name: str, monkeypatch
) -> Configuration:
    config = unittest.mock.create_autospec(Configuration)
    config.account_table_name = account_table_name
    config.region_name = "us-east-1"
    config.app_client_id = ""
    return config


@pytest.fixture()
@moto.mock_dynamodb
def _dynamodb_table(mocked_configuration: Configuration) -> Table:
    _dynamodb_resource = boto3.resource(
        "dynamodb", mocked_configuration.region_name
    )
    _dynamodb_table: Table = _dynamodb_resource.Table(
        mocked_configuration.account_table_name
    )
    return _dynamodb_table


@pytest.fixture()
@moto.mock_cognitoidp
def _cognito_client(
    mocked_configuration: Configuration,
) -> CognitoIdentityProviderClient:
    _cognito_client: CognitoIdentityProviderClient = boto3.client(
        "cognito-idp", mocked_configuration.region_name
    )
    return _cognito_client


@pytest.fixture()
def account_manager(
    mocked_configuration: Configuration,
    _dynamodb_table: Table,
    _cognito_client: CognitoIdentityProviderClient,
) -> AccountManager:
    return AccountManager(
        _dynamodb_table, _cognito_client, mocked_configuration, Logger()
    )


@pytest.fixture()
def setup_cognito_user_pool():
    @moto.mock_cognitoidp
    def _setup_cognito_user_pool() -> [str, str]:
        cognito_client: CognitoIdentityProviderClient = boto3.client(
            "cognito-idp", region_name="us-east-1"
        )
        user_pool_resp = cognito_client.create_user_pool(
            PoolName="passwordless-auth-user-pool",
            Schema=[
                {
                    "Name": "name",
                    "AttributeDataType": "String",
                    "Mutable": True,
                    "Required": True,
                },
                {
                    "Name": "email",
                    "AttributeDataType": "String",
                    "Mutable": True,
                    "Required": True,
                },
            ],
            UsernameAttributes=["email"],
            Policies={
                "PasswordPolicy": {
                    "MinimumLength": 8,
                    "RequireUppercase": False,
                    "RequireLowercase": False,
                    "RequireNumbers": False,
                    "RequireSymbols": False,
                }
            },
        )
        app_client_resp = cognito_client.create_user_pool_client(
            UserPoolId=user_pool_resp["UserPool"]["Id"],
            ClientName="email-auth-app-client",
            GenerateSecret=False,
            ExplicitAuthFlows=[
                "CUSTOM_AUTH_FLOW_ONLY",
            ],
        )
        return app_client_resp["UserPoolClient"]["ClientId"]

    return _setup_cognito_user_pool


@pytest.fixture()
def setup_dynamodb_table(
    account_table_name: str,
) -> Callable[[], None]:
    @moto.mock_dynamodb
    def _setup_dynamodb_table() -> None:
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")

        dynamodb.create_table(
            TableName=account_table_name,
            KeySchema=[
                {"AttributeName": "account_id", "KeyType": "HASH"},
            ],
            AttributeDefinitions=[
                {
                    "AttributeName": "account_id",
                    "AttributeType": "S",
                }
            ],
            ProvisionedThroughput={
                "ReadCapacityUnits": 10,
                "WriteCapacityUnits": 10,
            },
        )

    return _setup_dynamodb_table


@pytest.fixture()
def post_account_payload() -> PostAccount:
    return PostAccount.model_validate(
        {
            "first_name": "Bob",
            "last_name": "James",
            "email_address": "bob.james@example.com",
            "phone_number": "+442071234567",
        }
    )


@pytest.fixture
def lambda_context():
    @dataclass
    class LambdaContext:
        function_name: str = "test"
        memory_limit_in_mb: int = 128
        invoked_function_arn: str = (
            "arn:aws:lambda:eu-west-1:123456789012:function:test"
        )
        aws_request_id: str = "da658bd3-2d6f-4e7b-8ec2-937234644fdc"

    return LambdaContext()
