# Terraform  
Version: 1.8.4  
Updated: 2024-06-10  

### 1.Installation
install using brew  
```
brew tap hashicorp/tap
brew install hashicorp/tap/terraform
```

### 2.Usage
##### Build infrastructure
-   ```terraform init``` - initialize the project
-   ```terraform fmt``` - automatically updates configurations in the current directory for readability and consistency.
-   ```terraform validate``` - check configuration is syntactically valid and internally consistent.
-   ```terraform plan``` - prints out the execution plan which describes the actions Terraform will take in order to change your infrastructure to match the configuration
-   ```terraform apply ``` - apply the configuration. Before it applies any changes, Terraform prints out the execution plan which describes the actions Terraform will take in order to change your infrastructure to match the configuration.

##### Delete infrastructure
- ```terraform destroy -target RESOURCE_TYPE.NAME``` - destroy a specific resource

### 3. Terraform files

##### lock
```.terraform.lock.hcl```

The terraform init command prints out which version of the provider was installed. 
Terraform also creates a lock file named .terraform.lock.hcl which specifies the exact provider versions used, 
so that you can control when you want to update the providers used for your project.

##### State
When you applied your configuration, Terraform wrote data into a file called ```terraform.tfstate```. 

Terraform stores the IDs and properties of the resources it manages in this file, so that it can update or destroy those resources going forward.

The Terraform state file is the only way Terraform can track which resources it manages, and often contains sensitive information, so you must store your state file securely and restrict access to only trusted team members who need to manage your infrastructure. In production, we recommend storing your state remotely with HCP Terraform or Terraform Enterprise. Terraform also supports several other remote backends you can use to store and manage your state.

-   ```terraform show``` - Inspect the current state using terraform show
-   ```terraform state``` - advanced state management
-   ```terraform state list``` - list of the resources in your project's state




