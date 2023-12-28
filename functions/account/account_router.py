# Third-party
from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler.exceptions import NotFoundError
from aws_lambda_powertools.event_handler.router import Router

# First-party
from functions.account.account_manager import get_account_manager
from functions.account.models import PatchAccount, PostAccount

logger = Logger()
router = Router()


@router.post("/accounts")
def create_account() -> dict[str, str]:
    account_manager = get_account_manager()
    body = PostAccount.model_validate(router.current_event.json_body)
    result = account_manager.create_account(body)
    logger.info(f"Account ({result}) created")
    return {"result": str(result)}


@router.get("/accounts/<account_id>")
def get_account(account_id: str) -> dict[str, object]:
    account_manager = get_account_manager()
    account = account_manager.get_account(account_id)
    if account:
        logger.info(f"{account} found")
        return {"result": account.model_dump(mode="json")}
    raise NotFoundError("Account not found")


@router.patch("/accounts")
def patch_account() -> dict[str, str]:
    account_manager = get_account_manager()
    body = PatchAccount.model_validate(router.current_event.json_body)
    account_manager.patch_account(body)
    return {"result": "Update successfully"}
