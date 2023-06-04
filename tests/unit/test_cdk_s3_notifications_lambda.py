import re

import pytest
from aws_cdk import Stack, assertions
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_s3 as s3

from lib.aws_s3_patterns import S3NotificationsToLambda


def test_s3_notifications_created():
    stack = Stack()

    S3NotificationsToLambda(
        stack,
        "S3NotificationsToLambda",
        function=_lambda.Function(
            stack,
            "TestFunction",
            runtime=_lambda.Runtime.PYTHON_3_10,
            handler="hello.handler",
            # we're not testing the function's logic so the actual code is irrelevant
            code=_lambda.Code.from_inline('"code"'),
        ),
        bucket=s3.Bucket(stack, "TestBucket"),
        event_type=s3.EventType.OBJECT_CREATED,
    )

    template = assertions.Template.from_stack(stack)
    template.resource_count_is("Custom::S3BucketNotifications", 1)


def test_s3_notifications_created_with_right_event():
    stack = Stack()

    S3NotificationsToLambda(
        stack,
        "S3NotificationsToLambda",
        function=_lambda.Function(
            stack,
            "TestFunction",
            runtime=_lambda.Runtime.PYTHON_3_10,
            handler="hello.handler",
            # we're not testing the function's logic so the actual code is irrelevant
            code=_lambda.Code.from_inline('"code"'),
        ),
        bucket=s3.Bucket(stack, "TestBucket"),
        event_type=s3.EventType.OBJECT_REMOVED_DELETE,
    )

    template = assertions.Template.from_stack(stack)
    template.has_resource_properties(
        "Custom::S3BucketNotifications",
        {
            "NotificationConfiguration": {
                "LambdaFunctionConfigurations": [
                    {"Events": ["s3:ObjectRemoved:Delete"]}
                ]
            }
        },
    )


def test_s3_notifications_created_with_right_destination():
    stack = Stack()
    function: _lambda.IFunction = _lambda.Function(
        stack,
        "TestFunction",
        runtime=_lambda.Runtime.PYTHON_3_10,
        handler="hello.handler",
        # we're not testing the function's logic so the actual code is irrelevant
        code=_lambda.Code.from_inline('"code"'),
    )

    S3NotificationsToLambda(
        stack,
        "S3NotificationsToLambda",
        function=function,
        bucket=s3.Bucket(stack, "TestBucket"),
        event_type=s3.EventType.OBJECT_CREATED,
    )

    template = assertions.Template.from_stack(stack)
    function_name = assertions.Capture()

    template.has_resource_properties(
        "Custom::S3BucketNotifications",
        {
            "NotificationConfiguration": {
                "LambdaFunctionConfigurations": [
                    {"LambdaFunctionArn": {"Fn::GetAtt": [function_name, "Arn"]}}
                ]
            }
        },
    )

    assert re.match("^TestFunction", function_name.as_string())


def test_s3_notifications_one_function_permission_assigned():
    stack = Stack()
    function: _lambda.IFunction = _lambda.Function(
        stack,
        "TestFunction",
        runtime=_lambda.Runtime.PYTHON_3_10,
        handler="hello.handler",
        # we're not testing the function's logic so the actual code is irrelevant
        code=_lambda.Code.from_inline('"code"'),
    )
    bucket: s3.Bucket = s3.Bucket(stack, "TestBucket")

    S3NotificationsToLambda(
        stack,
        "S3NotificationsToLambda",
        function=function,
        bucket=bucket,
        event_type=s3.EventType.OBJECT_CREATED,
        function_permissions=[
            iam.PolicyStatement(
                actions=["s3:GetObject"],
                effect=iam.Effect.ALLOW,
                resources=[f"{bucket.bucket_arn}/*"],
            )
        ],
    )

    template = assertions.Template.from_stack(stack)
    bucket_name = assertions.Capture()

    template.has_resource_properties(
        "AWS::IAM::Policy",
        {
            "PolicyDocument": {
                "Statement": [
                    {
                        "Action": "s3:GetObject",
                        "Resource": {
                            "Fn::Join": [
                                "",
                                [{"Fn::GetAtt": [bucket_name, "Arn"]}, "/*"],
                            ]
                        },
                    }
                ]
            }
        },
    )

    assert re.match("^TestBucket", bucket_name.as_string())


def test_s3_notifications_multiple_function_permission_assigned():
    stack = Stack()
    function: _lambda.IFunction = _lambda.Function(
        stack,
        "TestFunction",
        runtime=_lambda.Runtime.PYTHON_3_10,
        handler="hello.handler",
        # we're not testing the function's logic so the actual code is irrelevant
        code=_lambda.Code.from_inline('"code"'),
    )
    bucket: s3.Bucket = s3.Bucket(stack, "TestBucket")

    S3NotificationsToLambda(
        stack,
        "S3NotificationsToLambda",
        function=function,
        bucket=bucket,
        event_type=s3.EventType.OBJECT_CREATED,
        function_permissions=[
            iam.PolicyStatement(
                actions=["s3:GetObject"],
                effect=iam.Effect.ALLOW,
                resources=[f"{bucket.bucket_arn}/*"],
            ),
            iam.PolicyStatement(
                actions=["s3:ListBucket"],
                effect=iam.Effect.ALLOW,
                resources=[bucket.bucket_arn],
            ),
        ],
    )

    template = assertions.Template.from_stack(stack)
    bucket_name = assertions.Capture()

    template.has_resource_properties(
        "AWS::IAM::Policy",
        {
            "PolicyDocument": {
                "Statement": [
                    {
                        "Action": "s3:GetObject",
                        "Resource": {
                            "Fn::Join": [
                                "",
                                [{"Fn::GetAtt": [bucket_name, "Arn"]}, "/*"],
                            ]
                        },
                    },
                    {
                        "Action": "s3:ListBucket",
                        "Resource": {"Fn::GetAtt": [bucket_name, "Arn"]},
                    },
                ]
            }
        },
    )

    assert re.match("^TestBucket", bucket_name.as_string())


def test_s3_notifications_invalid_policy_throws_assertion_error():
    stack = Stack()
    function: _lambda.IFunction = _lambda.Function(
        stack,
        "TestFunction",
        runtime=_lambda.Runtime.PYTHON_3_10,
        handler="hello.handler",
        # we're not testing the function's logic so the actual code is irrelevant
        code=_lambda.Code.from_inline('"code"'),
    )

    with pytest.raises(AssertionError):
        S3NotificationsToLambda(
            stack,
            "S3NotificationsToLambda",
            function=function,
            bucket=s3.Bucket(stack, "TestBucket"),
            event_type=s3.EventType.OBJECT_CREATED,
            function_permissions=["InvalidPolicy"],
        )
