#!/usr/bin/env bash

BUILD_SCRIPT_FILE_PATH="deploy-app.sh"
TERRAGRUNT_FILE_PATH="infrastructure/terragrunt.hcl"

help_function()
{
   echo ""
   echo "Usage: $0 -r AWS_REGION -p AWS_PROFILE"
   echo -e "\t- <AWS_REGION>"
   echo -e "\t-p <AWS_PROFILE>"
   exit 1 # Exit script after printing help
}

while getopts "r:p:" opt
do
   case "$opt" in
      r ) AWS_REGION="$OPTARG" ;;
      p ) AWS_PROFILE="$OPTARG" ;;
      ? ) help_function ;; # Print help_function in case parameter is non-existent
   esac
done

# Print help_function in case parameters are empty
if [ -z "$AWS_REGION" ] || [ -z "$AWS_PROFILE" ]
then
   echo "Some or all of the parameters are empty";
   help_function
fi

# Validate input
AWS_PROFILE="$(echo ${AWS_PROFILE} | tr '[:upper:]' '[:lower:]' | tr -cd '[:alnum:]_-')"
AWS_REGION="$(echo ${AWS_REGION} | tr '[:upper:]' '[:lower:]' | tr -cd '[:alnum:]_-')"

echo "AWS_REGION=$AWS_REGION"
echo "AWS_PROFILE=$AWS_PROFILE"

set_variables()
{

   export AWS_PROFILE=${AWS_PROFILE}
   export AWS_REGION=${AWS_REGION}
   if [ -f ${BUILD_SCRIPT_FILE_PATH} ] && [ -f ${TERRAGRUNT_FILE_PATH} ]; then
      # replace vars
      echo "Adding vars to ${BUILD_SCRIPT_FILE_PATH}"
      sed -i -e 's/aws_region/'${AWS_REGION}'/g' ${BUILD_SCRIPT_FILE_PATH}
      sed -i -e 's/aws_profile/'${AWS_PROFILE}'/g' ${BUILD_SCRIPT_FILE_PATH}

      echo "Adding vars to ${TERRAGRUNT_FILE_PATH}"
      sed -i -e 's/aws_region/'${AWS_REGION}'/g' ${TERRAGRUNT_FILE_PATH}
      sed -i -e 's/aws_profile/'${AWS_PROFILE}'/g' ${TERRAGRUNT_FILE_PATH}
    fi
}

set_variables