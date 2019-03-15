# infra-problem submission

## Prerequisites

* Java
* [Leiningen](http://leiningen.org/) (can be installed using `brew install leiningen`)
* AWS Account
* AWS cli configured on your system with admin privleges

## Deployment infrastructure and services

1. Launch an Fargate ECS cluster using the Cloudformation template:

   ```
   $ aws cloudformation deploy \
   --template-file infrastructure/infrastructure.yml \
   --region <region> \
   --stack-name <stack name> \
   --capabilities CAPABILITY_NAMED_IAM
   ```
2. Build clojure application jar files

3. Deploy the services as containers onto your cluster: 

   ```
   $ ./deploy.sh <region> <service name>
   ```

