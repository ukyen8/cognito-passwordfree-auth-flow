# Standard library
import logging

# Third-party
from aws_lambda_powertools.utilities.data_classes import event_source
from aws_lambda_powertools.utilities.data_classes.cognito_user_pool_event import \
    PreSignUpTriggerEvent
from aws_lambda_powertools.utilities.typing import LambdaContext

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@event_source(data_class=PreSignUpTriggerEvent)
def handler(event: PreSignUpTriggerEvent, context: LambdaContext):
    """Auto confirm user after user sign up.

    ..note::
        Only a confirmed user can invoke the custom authentication flow.
    """
    logger.info(f"{event.raw_event=}")
    event.response.auto_confirm_user = True
    return event.raw_event
