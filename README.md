# cognito-passwordfree-auth-flow

Implement password-free authentication flow with Amazon Cognito.
Sign-up and sign-in with email address only.

## Custom authentication flow script

`auth_flow_script.py` is a demo client for testing password-free authentication
flow. Run:

`python auth_flow_script.py`

It will prompt you to provide email address and a name.

```shell
Please input email: <Enter email address>  # e.g. john.wick@gmail.com
Please enter your name: <Enter a name>  # e.g. John Wick
```

If the email doesn't exist, the user will be created in AWS Cognito User Pool.

After a user is created, the script calls `initiate_auth_flow` function to
initiate authentication flow. If the provided details are correct, you will see
the following message:

```shell
An authentication code has been sent to john.wick@gmail.com, please enter it here.
Enter one-time 6-digits code: <Enter you code>
```

Please now go to the email inbox to copy the authentication code and paste it.
After a few seconds, you will see the authentication results on the console.

**Note:** Please replace `APP_CLIENT_ID` and `USER_POOL_ID` with the real values.
