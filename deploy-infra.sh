
#!/usr/bin/env bash
# Deploy infra using terragrunt

INFRA_DIR_NAME="infrastructure"

plan_infra() {
    echo "Checking if all files & directory exists"
    if [[ -d "$INFRA_DIR_NAME" ]]; then
        echo "Deploying Infrastructure..."
        terragrunt run-all plan --terragrunt-include-dir "$INFRA_DIR_NAME/"
    fi
    echo "Infrastructure deployed. Move on to build.sh & deploy.sh to build and deploy application"
}

deploy_infra() {
    echo "Checking if all files & directory exists"
    if [[ -d "$INFRA_DIR_NAME" ]]; then
        echo "Deploying Infrastructure..."
        terragrunt run-all apply --terragrunt-include-dir "$INFRA_DIR_NAME/"
        terragrunt output --terragrunt-config "$INFRA_DIR_NAME/terragrunt.hcl" > terragrunt_output.log
        echo "Infrastructure deployed. Move on to app.sh script"
    fi
}

destroy_infra() {
    if [[ -d "$INFRA_DIR_NAME" ]]; then
        echo "Destroying Infrastructure..."
        terragrunt run-all destroy --terragrunt-include-dir "$INFRA_DIR_NAME/"
    fi
}

plan_infra
deploy_infra
# destroy_infra