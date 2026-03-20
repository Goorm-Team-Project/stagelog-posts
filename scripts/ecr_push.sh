#!/usr/bin/env bash
set -euo pipefail

AWS_REGION="${AWS_REGION:-ap-northeast-2}"
ACCOUNT_ID="${ACCOUNT_ID:-430118823715}"
REPO="${REPO:-stagelog-posts}"
TAG="${TAG:-$(git rev-parse --short HEAD 2>/dev/null || echo latest)}"
IMAGE_LOCAL="${IMAGE_LOCAL:-stagelog-posts}"
ECR_URI="${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${REPO}"
SHARED_SOURCE_DIR="${SHARED_SOURCE_DIR:-../shared}"
SHARED_CONTEXT_DIR="${SHARED_CONTEXT_DIR:-_shared}"

cleanup() {
  rm -rf "${SHARED_CONTEXT_DIR}"
}

if [ ! -f "${SHARED_SOURCE_DIR}/pyproject.toml" ]; then
  echo "shared contracts not found: ${SHARED_SOURCE_DIR}" >&2
  exit 1
fi

trap cleanup EXIT
rm -rf "${SHARED_CONTEXT_DIR}"
cp -a "${SHARED_SOURCE_DIR}" "${SHARED_CONTEXT_DIR}"

aws ecr describe-repositories --repository-names "${REPO}" --region "${AWS_REGION}" >/dev/null 2>&1 || aws ecr create-repository --repository-name "${REPO}" --region "${AWS_REGION}"

aws ecr get-login-password --region "${AWS_REGION}" |   docker login --username AWS --password-stdin "${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

docker build -t "${IMAGE_LOCAL}:${TAG}" -f docker/api/Dockerfile .
docker tag "${IMAGE_LOCAL}:${TAG}" "${ECR_URI}:${TAG}"
docker tag "${IMAGE_LOCAL}:${TAG}" "${ECR_URI}:latest"

docker push "${ECR_URI}:${TAG}"
docker push "${ECR_URI}:latest"

echo "Pushed: ${ECR_URI}:${TAG}"
echo "Pushed: ${ECR_URI}:latest"
