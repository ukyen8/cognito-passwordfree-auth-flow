# Standard library
import http
import json
import uuid
from unittest.mock import MagicMock, patch

# Third-party
import dotenv
from aws_lambda_powertools.event_handler.api_gateway import LambdaContext

# First-party
from functions.account import lambda_handler
from functions.account.models import Account, PostAccount

dotenv.load_dotenv("tests/.test.env")


class TestLambdaHandler:
    @patch("functions.account.account_manager.AccountManager")
    def test_create_account(
        self,
        mocked_account_manager: MagicMock,
        post_account_payload: PostAccount,
        lambda_context: LambdaContext,
    ) -> None:
        mocked_account_manager.return_value.create_account.return_value = (
            "new-account-id"
        )
        event = {
            "path": "/accounts",
            "httpMethod": "POST",
            "body": post_account_payload.model_dump_json(),
        }
        result = lambda_handler.handler(event, lambda_context)
        assert result["statusCode"] == http.HTTPStatus.OK
        body = json.loads(result["body"])
        assert body == {"result": "new-account-id"}

    @patch("functions.account.account_manager.AccountManager")
    def test_patch_account(
        self,
        mocked_account_manager,
        lambda_context: LambdaContext,
    ) -> None:
        event = {
            "path": "/accounts",
            "httpMethod": "PATCH",
            "body": json.dumps(
                {"account_id": str(uuid.uuid4()), "first_name": "Jane"}
            ),
        }
        result = lambda_handler.handler(event, lambda_context)
        assert result["statusCode"] == http.HTTPStatus.OK

    @patch("functions.account.account_manager.AccountManager")
    def test_get_account(
        self,
        mocked_account_manager: MagicMock,
        lambda_context: LambdaContext,
    ) -> None:
        account_id = uuid.uuid4()
        expected_account = Account(
            account_id=account_id,
            first_name="John",
            last_name="Smith",
            email_address="example@gmail.com",
            phone_number="+442071234567",
        )
        mocked_account_manager.return_value.get_account.return_value = (
            expected_account
        )
        event = {
            "path": f"/accounts/{account_id}",
            "httpMethod": "GET",
        }
        result = lambda_handler.handler(event, lambda_context)
        assert result["statusCode"] == http.HTTPStatus.OK
        body = json.loads(result["body"])
        assert body == {"result": expected_account.model_dump(mode="json")}

    @patch("functions.account.account_manager.AccountManager")
    def test_get_account__not_found_error(
        self,
        mocked_account_manager: MagicMock,
        lambda_context: LambdaContext,
    ) -> None:
        mocked_account_manager.return_value.get_account.return_value = None
        event = {
            "path": "/accounts/not-existent-account-id",
            "httpMethod": "GET",
        }
        result = lambda_handler.handler(event, lambda_context)
        assert result["statusCode"] == http.HTTPStatus.NOT_FOUND

    @patch("functions.account.account_manager.AccountManager")
    def test_validation_error(
        self, mocked_account_manager: MagicMock, lambda_context: LambdaContext
    ) -> None:
        event = {
            "path": "/accounts",
            "httpMethod": "POST",
            "body": json.dumps({"account_id": "not-a-valida-account-id"}),
        }
        result = lambda_handler.handler(event, lambda_context)
        assert result["statusCode"] == http.HTTPStatus.UNPROCESSABLE_ENTITY
