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
   $ ./deploy.py <service name> <region>
   ```
5. Prereq before pushing Frontend service:

    ```
    open services/front-end/Dockerfile
    replace the URL for quotes and newsfeed with the loadbalancer url created after executing cloudformation template in Step 1

    ```
6.  Build & deploy Frontend service:

    ```
    $ ./deploy.py frontend <region>
    ```

