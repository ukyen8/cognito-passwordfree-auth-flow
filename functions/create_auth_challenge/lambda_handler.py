# Standard library
import logging
import random
import re

# Third-party
import boto3
from aws_lambda_powertools.utilities.data_classes import event_source
from aws_lambda_powertools.utilities.data_classes.cognito_user_pool_event import (
    CreateAuthChallengeTriggerEvent,
)
from aws_lambda_powertools.utilities.typing import LambdaContext

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ses_client = boto3.client("ses", region_name="us-east-2")


def send_mail(
    recipient: str,
    subject: str,
    body: str,
    sender: str = "wucean@gmail.com",
):
    ses_client.send_email(
        Destination={"ToAddresses": [recipient]},
        Message={
            "Body": {"Text": {"Charset": "utf-8", "Data": body}},
            "Subject": {"Charset": "utf-8", "Data": subject},
        },
        Source=sender,
    )


@event_source(data_class=CreateAuthChallengeTriggerEvent)
def handler(event: CreateAuthChallengeTriggerEvent, context: LambdaContext):
    """Create auth challenge by creating and sending auth code."""
    logger.info(f"{event.raw_event=}")
    recipient = event.request.user_attributes["email"]
    if not event.request.session:
        code = "".join(map(str, random.sample(range(0, 9), 6)))
        sent_message = (
            f"This is your one-time authentication code: {code}."
            f"It will expire in 3 minutes."
        )
        send_mail(
            recipient=recipient,
            subject="One-time authentication code",
            body=sent_message,
        )
    else:
        last_session = event.request.session[-1]
        code = re.search(
            r"AUTHCODE-(\d{6})", last_session.challenge_metadata
        ).group(1)

    event.response.private_challenge_parameters = {"challenge": code}
    event.response.challenge_metadata = f"AUTHCODE-{code}"

    return event.raw_event
