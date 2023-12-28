# Third-party
from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler import (
    APIGatewayRestResolver,
    Response,
    content_types,
)
from aws_lambda_powertools.utilities.typing import LambdaContext
from pydantic import ValidationError

# First-party
from functions.account import account_router

logger = Logger()
app = APIGatewayRestResolver()
app.include_router(account_router.router)


@app.exception_handler(ValidationError)
def handle_invalid_request_parameters(exc: ValidationError):
    metadata = {
        "path": app.current_event.path,
        "body": app.current_event.json_body,
    }
    logger.error(f"Bad request: {exc}", extra=metadata)

    return Response(
        status_code=422,
        content_type=content_types.APPLICATION_JSON,
        body="Invalid request parameters",
    )


@logger.inject_lambda_context
def handler(event: dict, context: LambdaContext):
    return app.resolve(event, context)
