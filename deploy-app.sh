#!/usr/bin/env bash


# Variables
AWS_PROFILE="aws_profile"
AWS_REGION="aws_region"
PRE_REQ_FILES="Makefile Dockerfile"
PRE_REQ_DIRS="front-end newsfeed quotes common-utils"
TERRAGRUNT_OUTPUTS_FILE="terragrunt_output.log"
HELM_PROJECT_DIR="clojure-app-charts"
HELM_CHART_NAME="clojure-app"

check_dependencies() {
    echo "Checking if all files & directory exists."
    
    for FILE in ${PRE_REQ_FILES}; do
        if ! [[ -f "${FILE}" ]]; then
            echo "${FILE} file not found. Required for this script."
        fi
    done

    for DIR in ${PRE_REQ_DIRS}; do
        if ! [[ -d "${DIR}" ]]; then
            echo "${DIR} directory not found. Required for this script."
        fi
    done
}

configure_eks() {
    EKS_CLUSTER_NAME=$(awk -v FS="cluster_name =" 'NF>1{print $2}' ${TERRAGRUNT_OUTPUTS_FILE} | tr -d '" ') 
    echo "Configuring ${EKS_CLUSTER_NAME} Cluster"
    if [[ -f ${TERRAGRUNT_OUTPUTS_FILE} ]]; then
        aws eks --region ${AWS_REGION} update-kubeconfig --name ${EKS_CLUSTER_NAME} --profile ${AWS_PROFILE}
        echo "Kubernetes configs updated."
    fi
}


run_tests() {
    if [[ -f "Makefile" ]]; then
        echo "Running Tests"
        make libs
        make test
        echo "Tests complete."
    fi
}

build_app() {
    if [[ -f "Makefile" ]]; then
        echo "Building & Testing Application"
        make libs
        make clean all
        echo "Building complete. Artifacts ready to be deployed"
    fi
}

build_docker_image() {
    # vars
    TAG_SUFFIX="$(echo $(date +%Y%m%d_%H%M%S) | tr '[:upper:]' '[:lower:]' | tr -cd '[:alnum:]._-')"
    ECR_REPOSITORY_URL=$(awk -v FS="ecr_repo_url =" 'NF>1{print $2}' ${TERRAGRUNT_OUTPUTS_FILE} | tr -d '" ')
    ECR_REPOSITORY_NAME=$(awk -v FS="ecr_repo_name =" 'NF>1{print $2}' ${TERRAGRUNT_OUTPUTS_FILE} | tr -d '"')

    ECR_URL="$(echo ${ECR_REPOSITORY_URL} | cut -d'/' -f1)"
    IMAGE_TAG="${ECR_REPOSITORY_URL}:${TAG_SUFFIX}"

    echo "Building Docker Image ${ECR_REPOSITORY_URL}"

    if ! [[ -z ${ECR_REPOSITORY_URL} ]]; then
        echo "Building image ${ECR_REPOSITORY_URL}"
        aws ecr get-login-password --region ${AWS_REGION} --profile ${AWS_PROFILE} | docker login -u AWS --password-stdin $ECR_URL
        docker build -t ${IMAGE_TAG} -t ${ECR_REPOSITORY_URL}:latest .
        docker push ${IMAGE_TAG}
        docker push ${ECR_REPOSITORY_URL}:latest
        echo "DEPLOY_VERSION=${TAG_SUFFIX}" >> image.env
        echo "ECR_REPOSITORY='${ECR_REPOSITORY_URL}'" >> image.env
        echo "Building complete. Image deployed to ${ECR_REPOSITORY_URL} Version ${TAG_SUFFIX} "
    fi
}

helm_deploy() {
  echo "Deploying HELM Charts"
  source image.env
  HELM_OVERRIDES="--set image.repository=${ECR_REPOSITORY},image.tag=${DEPLOY_VERSION}"

  #Fetch Image Version
  if ! [[ -z ${DEPLOY_VERSION} ]] ; then
        echo "Deploying Image Tag ${DEPLOY_VERSION} using HELM"
        echo "Deploying HELM chart ${HELM_CHART_NAME} using IMAGE TAG  ${ECR_REPOSITORY}:${DEPLOY_VERSION}"
        helm upgrade --atomic --cleanup-on-fail --install ${HELM_CHART_NAME} ${HELM_PROJECT_DIR} ${HELM_OVERRIDES}
        echo "Helm deployment complete"
        sleep 15
        export SERVICE_IP=$(kubectl get svc --namespace default frontend --template "{{ range (index .status.loadBalancer.ingress 0) }}{{.}}{{ end }}")
        echo "Service available at http://${SERVICE_IP}:8080"
        echo "It may take a few minutes for the LoadBalancer IP/URL to be available"
        
    fi
}

helm_test() {
  echo "Test Application Connection"
  helm test ${HELM_CHART_NAME}
}

helm_destroy() {
  echo "Destroying ${HELM_CHART_NAME}"
  helm uninstall ${HELM_CHART_NAME}
}

main() {
    check_dependencies
    configure_eks
    run_tests
    build_app
    build_docker_image
    helm_deploy
    # helm_test
    # helm_destroy
}

main "$@"

