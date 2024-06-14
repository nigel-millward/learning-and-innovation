# Localstack 
version 3.5

## 1.Installation
- brew install localstack/tap/localstack-cli
- brew install awscli-local
- install docker

## 2.Running

#### 2.1 localstack cli
```
localstack start -d
```

#### 2.2 docker compose
create a docker-compose yml file  
start localstack with the following command:
```
docker-compose up
```
## 3.Usage

#### 3.1 QuickStart
```
awslocal s3 mb s3://nigels-test-bucket
awslocal s3 ls
```

#### 3.2 Test utils
localstack provides test utils, to start and stop the container
```
pip install localstack-utils
```

### References
github page: https://github.com/localstack/localstack  
localstack docs: https://docs.localstack.cloud/overview/  
feature coverage: https://docs.localstack.cloud/user-guide/aws/feature-coverage/  
test utils: https://docs.localstack.cloud/user-guide/tools/testing-utils/


