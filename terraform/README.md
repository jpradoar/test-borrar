# Deploy terraform with MicroK8s ready for use

### Edit terraform vars


### Run terraform init and plan to see data
	terraform init && terraform plan


### Run terraform apply to deploy instance
	terraform apply -auto-approve


### To connect run
	terraform output connection|jq -r 