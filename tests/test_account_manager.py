# Standard library
from collections.abc import Callable

# Third-party
import moto
import pytest
from aws_lambda_powertools.event_handler.exceptions import BadRequestError
from mypy_boto3_dynamodb.service_resource import Table

# First-party
from functions.account.account_manager import AccountManager
from functions.account.config import Configuration
from functions.account.models import PatchAccount, PostAccount


@moto.mock_cognitoidp
@moto.mock_dynamodb
class TestAccountManager:

    def test_create_account(
        self,
        setup_cognito_user_pool: Callable[[], str],
        setup_dynamodb_table: Callable[[], None],
        post_account_payload: PostAccount,
        mocked_configuration: Configuration,
        account_manager: AccountManager,
    ) -> None:
        setup_dynamodb_table()
        mocked_configuration.app_client_id = setup_cognito_user_pool()

        result = account_manager.create_account(post_account_payload)
        assert result is not None

        with pytest.raises(BadRequestError):
            account_manager.create_account(post_account_payload)

    def test_get_account(
        self,
        setup_cognito_user_pool: Callable[[], str],
        setup_dynamodb_table: Callable[[], None],
        post_account_payload: PostAccount,
        mocked_configuration: Configuration,
        account_manager: AccountManager,
    ) -> None:
        setup_dynamodb_table()
        mocked_configuration.app_client_id = setup_cognito_user_pool()

        result = account_manager.create_account(post_account_payload)

        account = account_manager.get_account(str(result))
        assert account.id == result
        assert account.first_name == post_account_payload.first_name

    def test_patch_account(
        self,
        setup_cognito_user_pool: Callable[[], str],
        setup_dynamodb_table: Callable[[], None],
        post_account_payload: PostAccount,
        mocked_configuration: Configuration,
        account_manager: AccountManager,
        _dynamodb_table: Table,
    ):
        setup_dynamodb_table()
        mocked_configuration.app_client_id = setup_cognito_user_pool()

        result = account_manager.create_account(post_account_payload)
        original_item = _dynamodb_table.get_item(
            Key={"account_id": str(result)}
        )["Item"]

        patch_account_payload = PatchAccount(
            account_id=result, first_name="Jane"
        )
        account_manager.patch_account(patch_account_payload)

        updated_item = _dynamodb_table.get_item(
            Key={"account_id": str(result)}
        )["Item"]
        assert updated_item["first_name"] == "Jane"
        assert updated_item["modified_at"] > original_item["modified_at"]

        patch_account_payload.id = "non-existing-id"
        with pytest.raises(BadRequestError):
            account_manager.patch_account(patch_account_payload)
