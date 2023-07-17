# Standard library
import logging

# Third-party
from aws_lambda_powertools.utilities.data_classes import event_source
from aws_lambda_powertools.utilities.data_classes.cognito_user_pool_event import (
    ChallengeResult, DefineAuthChallengeTriggerEvent)
from aws_lambda_powertools.utilities.typing import LambdaContext

logger = logging.getLogger()
logger.setLevel(logging.INFO)

MAX_AUTH_RETRY = 3


def user_has_failed_authentication(session: list[ChallengeResult]) -> bool:
    """Check if the user provided a wrong answer for `MAX_AUTH_RETRY` times."""
    if (
        len(session) >= MAX_AUTH_RETRY
        and session[-1].challenge_name == "CUSTOM_CHALLENGE"
        and session[-1].challenge_result is False
    ):
        return True
    return False


def user_has_passed_authentication(session: list[ChallengeResult]) -> bool:
    """Check if the user provided the right answer."""
    if (
        session
        and len(session) <= MAX_AUTH_RETRY
        and session[-1].challenge_name == "CUSTOM_CHALLENGE"
        and session[-1].challenge_result is True
    ):
        return True
    return False


@event_source(data_class=DefineAuthChallengeTriggerEvent)
def handler(event: DefineAuthChallengeTriggerEvent, context: LambdaContext):
    """Define auth challenge by setting required flags."""
    logger.info(f"{event.raw_event=}")
    if user_has_failed_authentication(event.request.session):
        event.response.issue_tokens = False
        event.response.fail_authentication = True
    elif user_has_passed_authentication(event.request.session):
        event.response.issue_tokens = True
        event.response.fail_authentication = False
    else:
        # User hasn't provided a correct answer, present challenge
        event.response.issue_tokens = False
        event.response.fail_authentication = False
        event.response.challenge_name = "CUSTOM_CHALLENGE"

    return event.raw_event
