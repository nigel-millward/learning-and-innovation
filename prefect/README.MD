# Prefect Orchestation tool 


### Installation
Add the following to your requirements.txt file

```bash
anyio==4.4.0
prefect==2.20.3  
```

Run the following command on your virtual env:  
```bash
pip3 install -r requirements.txt 
```

Check installation details:  
```bash
prefect version
```

### QuickStart
1. Connect to prefects server api
```bash
prefect server start
```

Open the prefect dashboard in your browser with http://localhost:4200

2. Start the prefect script my_gh_workflow.py:
```bash
python my_gh_workflow.py
```

3. Create/run a workpool locally:
```bash
prefect work-pool create --type process my-work-pool
prefect work-pool ls
prefect worker start --pool my-work-pool
```

4. Deploy and schedule your flow with script create_deployment.py
```bash
python create_deployment.py
```

5. Schedule a run for the deployment
```bash
prefect deployment run 'repo-info/my-first-deployment'
```

### Develop overview

Write and run flows:  
https://docs-3.prefect.io/3.0rc/develop/write-flows

Write and run tasks:  
https://docs-3.prefect.io/3.0rc/develop/write-tasks

### DBT with Prefect

Integration:  
https://docs-3.prefect.io/integrations/prefect-dbt/index  

Blog:  
https://www.prefect.io/blog/dbt-and-prefect  
