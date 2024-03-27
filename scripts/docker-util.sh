VERB=$1

function build() {
  mkdir -p package
  poetry export -f requirements.txt -o package/requirements.txt --without-hashes
  docker build -t mood-tracker:latest .
}

function push() {
  commit_sha=$(git rev-parse --short HEAD)
  aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin "246770851643.dkr.ecr.eu-central-1.amazonaws.com"
  docker tag "mood-tracker:latest" "246770851643.dkr.ecr.eu-central-1.amazonaws.com/mood-tracker:latest"
  docker tag "mood-tracker:latest" "246770851643.dkr.ecr.eu-central-1.amazonaws.com/mood-tracker:${commit_sha}"
  docker push "246770851643.dkr.ecr.eu-central-1.amazonaws.com/mood-tracker:latest"
  docker push "246770851643.dkr.ecr.eu-central-1.amazonaws.com/mood-tracker:${commit_sha}"
}

$VERB