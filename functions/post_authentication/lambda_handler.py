# Standard library
import logging

# Third-party
import boto3
from aws_lambda_powertools.utilities.data_classes import event_source
from aws_lambda_powertools.utilities.data_classes.cognito_user_pool_event import (
    PostAuthenticationTriggerEvent,
)
from aws_lambda_powertools.utilities.typing import LambdaContext

logger = logging.getLogger()
logger.setLevel(logging.INFO)


client = boto3.client("cognito-idp", region_name="us-east-2")


@event_source(data_class=PostAuthenticationTriggerEvent)
def handler(event: PostAuthenticationTriggerEvent, context: LambdaContext):
    """Execute custom logics after authentication."""
    logger.info(f"{event.raw_event=}")
    if event.request.user_attributes["email_verified"] != "true":
        client.admin_update_user_attributes(
            UserPoolId=event.user_pool_id,
            UserAttributes=[{"Name": "email_verified", "Value": "true"}],
            Username=event.user_name,
        )
    return event.raw_event
