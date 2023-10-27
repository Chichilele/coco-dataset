#!/bin/bash
set -e 

# build a docker image and push to local demo registry of flyte


export VERSION="0.1.0"
export IMAGE_NAME=localhost:30000/coco-dataset:${VERSION}
export DOCKER_BUILDKIT=1

docker build -t ${IMAGE_NAME} \
  --target runtime \
  --build-arg tag=${VERSION} \
  --secret id=AWS_ACCESS_KEY_ID \
  --secret id=AWS_SECRET_ACCESS_KEY \
  --secret id=AWS_SESSION_TOKEN \
  --secret id=AWS_DEFAULT_REGION \
  .

docker push ${IMAGE_NAME}
pyflyte register workflows/example.py --image ${IMAGE_NAME} --version ${VERSION}
pyflyte register workflows/custom.py --image ${IMAGE_NAME} --version ${VERSION}
