#!/bin/bash

# by https://cheste.rs/cleaning-public-ecr-repositories-without-lifecycle-policies/

REPOSITORY_NAME=mood-tracker

IMAGES=$(aws ecr-public describe-images \
  --repository-name $REPOSITORY_NAME \
  --region us-east-1 | jq -r .imageDetails)

UNTAGGED_IMAGES=$(jq -r 'map(select(has("imageTags") | not))' <<< "$IMAGES")

echo "$UNTAGGED_IMAGES"

IMAGE_DIGESTS=$(jq -r '[.[] | "imageDigest=\(.imageDigest)"] | join(" ")' <<< "$UNTAGGED_IMAGES")
aws ecr-public batch-delete-image \
  --repository-name $REPOSITORY_NAME \
  --image-ids "$IMAGE_DIGESTS" \
  --region us-east-1
