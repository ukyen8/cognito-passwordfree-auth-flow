# Standard library
import dataclasses
import random
import string

# Third-party
import boto3


@dataclasses.dataclass
class AuthenticationResult:
    AccessToken: str
    ExpiresIn: int
    TokenType: str
    RefreshToken: str
    IdToken: str


cognito_client = boto3.client("cognito-idp", region_name="us-east-2")
APP_CLIENT_ID = "6qql5aaikn9eb6rn8f6031i7gu"  # Dev Cognito client
USER_POOL_ID = "us-east-2_znRmmh9VF"  # Dev Cognito user pool


def check_user_exist(email: str) -> bool:
    response = cognito_client.list_users(
        UserPoolId=USER_POOL_ID,
        Filter=f"email='{email}'",
    )
    return True if response["Users"] else False


def create_user(email: str, name: str):
    try:
        cognito_client.sign_up(
            ClientId=APP_CLIENT_ID,
            Username=email,
            Password="".join(random.choice(string.ascii_letters) for i in range(8)),
            UserAttributes=[
                {
                    "Name": "name",
                    "Value": name,
                },
            ],
        )
    except Exception as e:
        print(e)
    else:
        print(f"User {email} created!")


def initiate_auth_flow(email) -> str:
    response = cognito_client.initiate_auth(
        ClientId=APP_CLIENT_ID,
        AuthFlow="CUSTOM_AUTH",
        AuthParameters={
            "USERNAME": email,
        },
    )
    return response["Session"]


def answer_challenge(email: str, session_id: str) -> AuthenticationResult:
    while True:
        auth_code = input("Enter one-time 6-digits code: ")
        response = cognito_client.respond_to_auth_challenge(
            ClientId=APP_CLIENT_ID,
            ChallengeName="CUSTOM_CHALLENGE",
            Session=session_id,
            ChallengeResponses={
                "USERNAME": email,
                "ANSWER": auth_code,
            },
        )
        print(f"{response['ChallengeParameters']=}")
        if not response["ChallengeParameters"]:
            break
        session_id = response["Session"]
    return AuthenticationResult(**response["AuthenticationResult"])


if __name__ == "__main__":
    email = input("Please input email: ")
    name = input("Please enter your name: ")
    if not check_user_exist(email):
        print(f"User: {email} does not exist, create a new one")
        create_user(email, name)
    else:
        print(f"User: {email} exits")
    session_id = initiate_auth_flow(email)

    print(f"An authentication code has been sent to {email}, please enter it here.")
    authentication_result = answer_challenge(email, session_id)
    print(f"{authentication_result.IdToken=}")
    print(f"{authentication_result.AccessToken=}")
    print(f"{authentication_result.RefreshToken=}")
    print(f"{authentication_result.ExpiresIn=}")
    print(f"{authentication_result.TokenType=}")
