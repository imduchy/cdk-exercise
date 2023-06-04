from aws_cdk import (
    Stack,
    aws_ecs as ecs,
    aws_ec2 as ec2,
    aws_ecs_patterns as ecs_patterns,
)
from constructs import Construct


class CdkEcsStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc = ec2.Vpc(self, "TestVpc", max_azs=2)
        cluster = ecs.Cluster(self, "TestCluster", vpc=vpc, cluster_name="TestCluster")
        _ = ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            "TestAlbFargateService",
            cluster=cluster,
            public_load_balancer=True,
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_registry("amazon/amazon-ecs-sample")
            ),
        )
