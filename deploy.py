import os
import subprocess
import sys

import boto3
import base64

# List
service_list = ['front-end', 'quotes', 'newsfeed',]

# Initialize services
ecs_client = boto3.client('ecs')
ecr_client = boto3.client('ecr')
cfn_client = boto3.client('cloudformation')
elb_client = boto3.client('elbv2')


def check_ecr_repo(serviceName):
    # Check if ECR repo exists

    repo_list = []
    ecr_repos = ecr_client.describe_repositories()
    for repo in ecr_repos['repositories']:
        repo_list.append(repo['repositoryName'])
    if serviceName in repo_list:
        print("Matched!")
        return True
    else:
        print("ECR [{}] reposiroty not found!".format(serviceName))
        return False


def create_ecr_repo(serviceName):
    # Create ECR repo

    response = input("Do you want to create a new ECR repo named {} ? y or n : ".format(serviceName))

    if response == 'y' or response == 'yes':
        output = ecr_client.create_repository(repositoryName= serviceName)
        print("Created [{}] ECR repository.".format(serviceName))
        print("Name: ", output['repository']['repositoryName'])
        print("URL: ", output['repository']['repositoryUri'])
        repo_name = output['repository']['repositoryName']
        repo_uri = output['repository']['repositoryUri']
    else:
        print("Skipping everything.")
        repo_name = None
        repo_uri = None
    return(repo_name, repo_uri)


def build_docker_image(serviceName, repo_uri):
    # Build Docker images

    path = os.path.expanduser('services')
    print("Looking for service directory under /services...")
    if serviceName in os.listdir(path):
        print("File matched!")
        try:
            print("Building docker images...")
            subprocess.run(['docker-compose', '-f', 'services/docker-compose.yml', 'build'])
            push_docker_image(serviceName, repo_uri)
        except OSError:
            print("Issue creating docker images. Pls check dockerfile's")
    else:
        print("{} file not found in {}".format(serviceName, path))
    return


def fetch_repo_info(serviceName):
    # Fetch ECR repo information

    try:
        output = ecr_client.describe_repositories(repositoryNames=[serviceName])
        print("Fetching info for [{}] ECR repository....".format(serviceName))

        for repo in output['repositories']:
            if repo['repositoryName'] == serviceName:
                print("Name: ", repo['repositoryName'])
                print("URL: ", repo['repositoryUri'])
                repo_uri = repo['repositoryUri']
                break
    except Exception:
        print("Problem fetching info for {} ECR repo".format(serviceName))
    return(repo_uri)


def push_docker_image(serviceName, repo_uri):
    # Push docker image to ecr repo

    repo_url = "https://{}".format(repo_uri)
    print("URL", repo_url)

    if repo_uri and serviceName:
        try:
            print("Pushing docker image of {} ...".format(serviceName))

            # # ECR login
            # login_creds = subprocess.run(['$','(','aws', 'ecr', 'get-login', '--no-include-email',')'])

            # Make tags
            local_image_tag = "services_{}:latest".format(serviceName)
            print(local_image_tag)
            remote_image_tag = "{}:latest".format(repo_uri, serviceName)
            print(remote_image_tag)

            # Tag and push ECR image
            subprocess.run(['docker', 'tag', local_image_tag, remote_image_tag])
            subprocess.run(['docker', 'push', remote_image_tag])
        except Exception:
            print("Problem while pushing images")
    return


def get_cfn_output(stack_name):
    # Get output values of cloudformation template
    
    output_values = []
    if stack_name:
        try:
            output = cfn_client.describe_stacks(StackName=stack_name)
            for key in output['Stacks'][0]['Outputs']:
                output_values.append([key['OutputKey'], key['OutputValue']])

            for value in output_values:
                if 'ECSServiceRole' in value:
                    EcsServiceRole = value[1]
                elif 'ECSTaskExecRole' in value:
                    EcsTaskExecRole = value[1]
                elif 'ClusterName' in value:
                    ClusterName = value[1]
                elif 'Url' in value:
                    Url = value[1]
                elif 'ALBArn' in value:
                    AlbArn = value[1]
                elif 'VPCId' in value:
                    VpcId = value[1]
                elif 'ECSSecurityGroupId' in value:
                    ECSSecurityGroupId = value[1]
                elif 'ALBName' in value:
                    AlbName = value[1]
                elif 'FrontendTargetGroupArn' in value:
                    FrontendTargetGroupArn = value[1]
                elif 'NewsfeedTargetGroupArn' in value:
                    NewsfeedTargetGroupArn = value[1]
                elif 'QuotesTargetGroupArn' in value:
                    QuotesTargetGroupArn = value[1]
        except KeyError:
            print(" Can't find cloudformation stack with name {}".format(stack_name))
    return(
        EcsServiceRole, 
        EcsTaskExecRole, 
        ClusterName, 
        Url, 
        AlbArn, 
        VpcId, 
        ECSSecurityGroupId, 
        AlbName,
        FrontendTargetGroupArn,
        NewsfeedTargetGroupArn,
        QuotesTargetGroupArn)


def register_task_defination(serviceName, EcsTaskExecRole, RepoUri, Port):

    if serviceName and EcsTaskExecRole and RepoUri and Port:
        try:
            ecs_client.register_task_definition(
                family='{}-taskdefination'.format(serviceName),
                executionRoleArn=EcsTaskExecRole,
                networkMode='awsvpc',
                containerDefinitions=[
                    {
                        "portMappings": [
                            {
                                "hostPort": int(Port),
                                "protocol": "tcp",
                                "containerPort": int(Port)
                            }
                        ],
                        "memoryReservation": 512,
                        "image": "{}:latest".format(RepoUri),
                        "name": "{}-service-container".format(serviceName)
                    }
                ],
                requiresCompatibilities=['FARGATE'],
                cpu='256',
                memory='512'
            )
        except Exception:
            print("Issue while registering task defination.")
    return


def create_task_defination(serviceName, stack_name, repo_uri, EcsTaskExecRole, VpcId):
    # create task defination

    quote_app_port = '8002'
    newsfeed_app_port = '8001'
    frontend_app_port = '8080'

    if serviceName == 'quotes':
        print("Creating Task Defination for Quotes!")
        register_task_defination(serviceName, EcsTaskExecRole, repo_uri, quote_app_port)

    elif serviceName == 'newsfeed':
        print("Creating Task Defination for Newfeed!")
        register_task_defination(serviceName, EcsTaskExecRole, repo_uri, newsfeed_app_port)

    elif serviceName == 'front-end':
        print("Creating Task Defination for Front-end!")
        register_task_defination(serviceName, EcsTaskExecRole, repo_uri, frontend_app_port)
    else:
        print("Issue Creating Task Defination.")
    return


def get_subnet_id(VpcId):
    # Get subnet ids
    subnet_list = []
    ec2 = boto3.resource('ec2')
    vpc = ec2.Vpc(VpcId)
    subnets = list(vpc.subnets.all())

    if len(subnets) > 0:
        for subnet in subnets:
            subnet_list.append((subnet.id))
    else:
        print("There is no subnet in this VPC!")
    return(subnet_list)


def create_ecs_service(
    clusterName, 
    serviceName,  
    loadBalancerName,
    subnet,
    securityGroup,
    FrontendTargetGroupArn,
    NewsfeedTargetGroupArn,
    QuotesTargetGroupArn
    ):

    # Create ecs service
    quote_app_port = '8002'
    newsfeed_app_port = '8001'
    frontend_app_port = '8080'

    if serviceName == 'quotes':
        print("Creating ECS service for Quotes!")
        containerName = 'quotes-container-service'
        taskDefinition = '{}-taskdefination'.format(serviceName)
        targetGroupArn = QuotesTargetGroupArn

        launch_fargate_service(
            clusterName, 
            serviceName, 
            taskDefinition,
            loadBalancerName,
            containerName,
            subnet,
            securityGroup,
            targetGroupArn,
            quote_app_port)

    elif serviceName == 'newsfeed':
        containerName = 'newfeed-container-service'
        print("Creating ECS service for NewsFeed!")
        taskDefinition = '{}-taskdefination'.format(serviceName)
        targetGroupArn = NewsfeedTargetGroupArn

        launch_fargate_service(
            clusterName, 
            serviceName, 
            taskDefinition,
            loadBalancerName,
            containerName,
            subnet,
            securityGroup,
            targetGroupArn,
            newsfeed_app_port)

    elif serviceName == 'front-end':
        containerName = 'front-end-container-service'
        print("Creating ECS service for Frontend!")
        taskDefinition = '{}-taskdefination'.format(serviceName)
        targetGroupArn = FrontendTargetGroupArn

        launch_fargate_service(
            clusterName, 
            serviceName, 
            taskDefinition,
            loadBalancerName,
            containerName,
            subnet,
            securityGroup,
            targetGroupArn,
            frontend_app_port)
    else:
        print("Unknown service name.")
    return

def launch_fargate_service(
    clusterName, 
    serviceName, 
    taskDefinition, 
    loadBalancerName,
    containerName,
    subnet,
    securityGroup,
    targetGroupArn,
    containerPort):

    # launch fargate service
    response = ecs_client.create_service(
        cluster=clusterName,
        serviceName=serviceName,
        taskDefinition=taskDefinition,
        loadBalancers=[
            {
                'targetGroupArn': str(targetGroupArn),
                'containerName': '{}-service-container'.format(serviceName),
                'containerPort': int(containerPort)
            }
        ],
        desiredCount=1,
        launchType='FARGATE',
        deploymentConfiguration={
            'maximumPercent': 200,
            'minimumHealthyPercent': 100
        },
        networkConfiguration={
            'awsvpcConfiguration': {
                'subnets': [
                    subnet[0],
                    subnet[1],
                ],
                'securityGroups': [
                    securityGroup,
                ],
                'assignPublicIp': 'ENABLED'
            }
        },
        healthCheckGracePeriodSeconds=123,
        schedulingStrategy='REPLICA'
    )

def run(stackName, serviceName, region):
    
    if stackName and serviceName and region:
        print("Validating service name...")
        if serviceName in service_list:
            
            print("Checking service name.. ", serviceName)
            status = check_ecr_repo(serviceName)
            if status is not True:
                create_ecr_repo(serviceName)

            repo_uri = fetch_repo_info(serviceName)
            build_docker_image(serviceName, repo_uri)
            
            # Get cloudformation output values
            output = get_cfn_output(stackName)
            EcsServiceRole = output[0]
            EcsTaskExecRole = output[1]
            ClusterName = output[2]
            Url = output[3]
            AlbArn = output[4]
            VpcId = output[5]
            ECSSecurityGroupId = output[6]
            AlbName = output[7]
            FrontendTargetGroupArn = output[8]
            NewsfeedTargetGroupArn = output[9]
            QuotesTargetGroupArn = output[10]

            # Create task defination
            create_task_defination(
                serviceName, 
                stackName, 
                repo_uri, 
                EcsTaskExecRole, 
                VpcId)

            # Fetch subnet ids
            if VpcId:
                subnets = get_subnet_id(VpcId)
            
            # Create ECS service
            create_ecs_service(
                ClusterName, 
                serviceName,
                AlbName,
                subnets,
                ECSSecurityGroupId,
                FrontendTargetGroupArn,
                NewsfeedTargetGroupArn,
                QuotesTargetGroupArn)
        else:
            print("Invalid service name entered.")
        return

if __name__ == '__main__':
    run(sys.argv[1], sys.argv[2], sys.argv[3])
