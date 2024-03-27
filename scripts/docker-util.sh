VERB=$1

function build() {
  mkdir -p package
  poetry export -f requirements.txt -o package/requirements.txt --without-hashes
  docker build -t mood-tracker:latest .
}

function push() {
  commit_sha=$(git rev-parse --short HEAD)
  aws ecr-public get-login-password --region us-east-1 | docker login --username AWS --password-stdin public.ecr.aws/c1o1h8f4
  docker tag mood-tracker:latest public.ecr.aws/c1o1h8f4/mood-tracker:latest
  docker tag mood-tracker:latest "public.ecr.aws/c1o1h8f4/mood-tracker:${commit_sha}"
  docker push public.ecr.aws/c1o1h8f4/mood-tracker:latest
  docker push "public.ecr.aws/c1o1h8f4/mood-tracker:${commit_sha}"
}

$VERB