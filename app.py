#!/usr/bin/env python3
import os

import aws_cdk as cdk

from cdk_ecs.cdk_ecs_stack import CdkEcsStack
from cdk_s3_notifications_lambda.cdk_s3_notifications_lambda_stack import (
    CdkS3NotificationsToLambdaStack,
)


app = cdk.App()

# CdkEcsStack(
#     app,
#     "CdkEcsStack",
#     env=cdk.Environment(
#         account=os.getenv("CDK_DEFAULT_ACCOUNT"), region=os.getenv("CDK_DEFAULT_REGION")
#     ),
# )

CdkS3NotificationsToLambdaStack(
    app,
    "CdkS3NotificationsToLambdaStack",
    env=cdk.Environment(
        account=os.getenv("CDK_DEFAULT_ACCOUNT"), region=os.getenv("CDK_DEFAULT_REGION")
    ),
)

app.synth()
