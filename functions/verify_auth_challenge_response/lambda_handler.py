# Standard library
import logging

# Third-party
from aws_lambda_powertools.utilities.data_classes import event_source
from aws_lambda_powertools.utilities.data_classes.cognito_user_pool_event import \
    VerifyAuthChallengeResponseTriggerEvent
from aws_lambda_powertools.utilities.typing import LambdaContext

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@event_source(data_class=VerifyAuthChallengeResponseTriggerEvent)
def handler(event: VerifyAuthChallengeResponseTriggerEvent, context: LambdaContext):
    """Verify auth challenge by checking user provided challenge answer."""
    logger.info(f"{event.raw_event=}")
    expected_answer = event.request.private_challenge_parameters.get("challenge")
    if event.request.challenge_answer == expected_answer:
        event.response.answer_correct = True
    else:
        event.response.answer_correct = False

    return event.raw_event
