from os import path
from aws_cdk import Stack, Tags, aws_s3 as s3, aws_lambda as lambda_, aws_iam as iam
from constructs import Construct
from lib import aws_s3_patterns as s3_patterns


class CdkS3NotificationsToLambdaStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        func = lambda_.Function(
            self,
            "TestLambda",
            function_name="testlambda",
            runtime=lambda_.Runtime.PYTHON_3_10,
            handler="service.lambda_handler",
            code=lambda_.Code.from_asset(
                path.join(path.dirname(path.abspath(__file__)), "lambda-handler")
            ),
        )
        bucket = s3.Bucket(self, "Bucket")

        func_permissions = [
            iam.PolicyStatement(
                actions=["s3:GetObject"],
                resources=[f"{bucket.bucket_arn}/*"],
                effect=iam.Effect.ALLOW,
            )
        ]

        notification = s3_patterns.S3NotificationsToLambda(
            self,
            "TestS3NotificationsToLambda",
            function=func,
            bucket=bucket,
            event_type=s3.EventType.OBJECT_CREATED,
            function_permissions=func_permissions,
        )

        Tags.of(func).add("project", "aws_cdk_exercise")
        Tags.of(bucket).add("project", "aws_cdk_exercise")
        Tags.of(notification).add("project", "aws_cdk_exercise")
