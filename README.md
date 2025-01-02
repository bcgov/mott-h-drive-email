# H-Drive-Email

## Deploying New Code
The build.yml github action will build the Dockerfile and push it to the OpenShift ImageStream you have configured.
Before you can run the workflow, ensure you have these variables and secrets configured:
- `OPENSHIFT_IMAGESTREAM_URL` variable
    - Looks like `image-registry.apps.silver.devops.gov.bc.ca/NAMESPACE/` (including -dev, test, prod or tools)
- `OPENSHIFT_IMAGESTREAM_USERNAME` secret
    - You can use the Pipeline user
- `OPENSHIFT_IMAGESTREAM_TOKEN` secret
    - You can use the Pipeline Token

## Other Configuration Required
- Deployment
- Service (if there is a UI)
- Route (if there is a UI)
- PVC (if required)
- Network Policies to allow inbound traffic (if required)




