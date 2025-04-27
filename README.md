# <img src="https://raw.githubusercontent.com/joeldsouza28/qubemech/refs/heads/f/logo/frontend/src/icons/logo2.svg" alt="Alt text" width="30" height="30"> QubeMech

QubeMech is multi cloud cluster management tool that allows you to manage cluster across different cloud providers. As of now it supports Azure and GCP. The image was made with the aim of simplifying cross cloud cluster management. The image makes use of terraform as an IaC provisioner. During the creation of a k8 cluster stream of logs is made possible with this image giving us the state of the cluster in real time. It allows us to list clusters across different projects in GCP and subscriptions in Azure. The authentication of the tool is done through Github Oauth. 

### Environment
###### Below are the environment variable that need to be set in order run the docker image
1. DB_URL (database url where service account configurations, remote backend configuration or service principal configuration are to be stored)
2. GITHUB_CLIENT_ID (client id of your github oauth app)
3. GITHUB_CLIENT_SECRET (client secret of your github oauth app)
4. HOST (this is the host that needs to be set to 0.0.0.0 in order for the running container to be accessible)

###### Below is the full command of running the docker image

```
docker run \
-e GITHUB_CLIENT_ID=<github client id> \
-e GITHUB_CLIENT_SECRET=<github client secret> \
-e DB_URL=<database url> \
-e host=0.0.0.0 \
-p 8000:80 \
-d joelreuben/qubemech:v1.0.0
```

### Tech

There are three aspects to the tech used in this project. The backend, the frontend and the IaC (Terraform). The structure of this project is as below
```
backend/
frontend/
infra/
```

The backend is entirely made in fastapi library for the api server and different cloud management libraries of azure and gcp. The frontend is built using react and tailwind css. The infra code is written keeping gcp and azure terraform provider syntax in mind.

[QubeMech Docker Image](https://hub.docker.com/r/joelreuben/qubemech)