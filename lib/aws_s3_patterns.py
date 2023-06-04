import aws_cdk.aws_iam as iam
import aws_cdk.aws_s3 as s3
import aws_cdk.aws_s3_notifications as s3_notifications
import aws_cdk.aws_lambda as lambda_
from constructs import Construct


class S3NotificationsToLambda(Construct):
    """An S3 bucket with an event notification triggering a Lambda function

    By default, if no function_permissions argument is specified, the Lambda function
    will be configured with no permissions over the S3 bucket.

    Example::

        # bucket: s3.Bucket
        # function: lambda_.Function
        # policies: list[iam.PolicyStatement]

        s3_patterns.S3NotificationsToLambda(
            self,
            "TestS3NotificationsToLambda",
            function=func,
            bucket=bucket,
            event_type=s3.EventType.OBJECT_CREATED,
            function_permissions=policies,
        )
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        function: lambda_.IFunction,
        bucket: s3.IBucket,
        event_type: s3.EventType,
        function_permissions: list[iam.PolicyStatement] = None,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        bucket.add_event_notification(
            event=event_type, dest=s3_notifications.LambdaDestination(function)
        )

        # The lambda:InvokeFunction permission is automatically added to the execution
        # role of the function, and assigned to the S3 bucket principal.
        # bucket_principal = iam.ServicePrincipal(
        #     service="s3.amazonaws.com",
        #     conditions=(
        #         {
        #             "ArnLike": {"aws:SourceArn": bucket.bucket_arn},
        #             "StringEquals": {
        #                 "AWS:SourceAccount": os.getenv("CDK_DEFAULT_ACCOUNT")
        #             },
        #         }
        #     ),
        # )
        # function.grant_invoke(bucket_principal)

        if function_permissions:
            for policy in function_permissions:
                assert isinstance(
                    policy, iam.PolicyStatement
                ), "The function_permissions argument must be a list of iam.PolicyStatement"

                function.add_to_role_policy(statement=policy)
