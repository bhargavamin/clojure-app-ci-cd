# infra-problem submission

## Prerequisites

* Java
* [Leiningen](http://leiningen.org/) (can be installed using `brew install leiningen`)
* AWS Account
* AWS cli configured on your system with admin privleges
* Python 2.7/3.6/3.7
* Boto3 package (`pip install boto3`)

## Deployment infrastructure and services

1. Launch an Fargate ECS cluster using the Cloudformation template:

   ```
   $ aws cloudformation deploy \
   --template-file infrastructure/infrastructure.yml \
   --region <region> \
   --stack-name <stack name> \
   --capabilities CAPABILITY_NAMED_IAM
   ```
2. Build clojure application jar files. Go to `services/' and run following commands

    ```
    $ make libs
    $ make clean all
    ```
This will generate jar files used in docker images.

3. Login to ECR

    ```
    $ $(aws ecr get-login --no-include-email --region <region>)
    ```
Note: the ecr login will be valid for 12 hours

4. Deploy Quotes and Newsfeed services as containers onto your cluster: 

   ```
   $ ./deploy.py <stack_name> <service name> <region>
   ```
5. Prereq before pushing Frontend service:

    ```
    open services/front-end/Dockerfile
    replace the URL for quotes and newsfeed with the loadbalancer url created after executing cloudformation template in Step 1

    ```
6.  Build & deploy Frontend service:

    ```
    $ ./deploy.py <stack_name> frontend <region>
    ```


# Future additions and evolutions

Suggestions for Infrastructure CI/CD

- Suggestions extend development environment to multiple/production environments:
 * Create separate account for each environment
 * Split cloudformation template as per services like `alb.yml, iam-role.yml ecs.yml etc`.
 * Create a code pipeline template to include all the above services cloudformation templates in stages.
 * Introduce cloudformation parameters which take environment as variables.
 * Put conditions in templates if you want to limit creation/deployment of resources to a particular environment.
 This way any infrastructure changes first gets deployed in development environment and if there is any issue the codepipeline stops execution and cloudformation rollbacks all the changes.

Suggestions for CI/CD of applications changes
- Suggestions to setup continous delivery:
 * Use Jenkins of Codebuild to setup a polling job to fetch all the latest code changes
 * A Jenkins or Codebuild job would build all the latest changes 
    - Use AWS SSM or Jenkins secrets to inject secrets or variables while building
 * Use the build artifact to deploy to a specific environment
    - There are multiple ways to deploy application changes using:
        - Deployment plugins and tools 
        - You can push changes on a versioned AWS S3 bucket which will tried codedeploy to deploy new changes
        - Better to have separate buckets for each environment to upload artifacts.
 