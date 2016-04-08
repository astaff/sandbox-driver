#!/bin/bash
# Expected environment variables
# 
# AWS_ACCESS_KEY_ID
# AWS_SECRET_ACCESS_KEY
# AWS_BUCKET
# ARCH : architecture: x86 or arm
# REPO : name of dockerhub repo
# NAME : name of the component to be used in container name and s3 file

# exit on first error to avoid
# errors snowballing
set -o errexit

# Install AWS cli
pip install awscli

for n in common common-build
do
  aws s3 cp s3://$AWS_BUCKET/builds/$n-$ARCH/latest/$REPO-$n-$ARCH.tar.gz - | gunzip | docker load && docker tag -f $REPO/$n-$ARCH $n
done

docker build -t $REPO/$NAME-$ARCH -f Dockerfile-build . \
&& docker run $REPO/$NAME-$ARCH > root.tar.gz \
&& docker build -t $REPO/$NAME-$ARCH -f Dockerfile-dist . \
&& docker save $REPO/$NAME-$ARCH | gzip | aws s3 cp - s3://$AWS_BUCKET/builds/$NAME-$ARCH/$TRAVIS_BUILD_NUMBER/$REPO-$NAME-$ARCH.tar.gz \
&& aws s3 rm s3://$AWS_BUCKET/builds/$NAME-$ARCH/latest --recursive \
&& aws s3 cp s3://$AWS_BUCKET/builds/$NAME-$ARCH/$TRAVIS_BUILD_NUMBER s3://$AWS_BUCKET/builds/$NAME-$ARCH/latest/ --recursive
