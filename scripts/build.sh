mkdir -p package

poetry export -f requirements.txt -o package/requirements.txt --without-hashes
docker build -t mood-tracker:latest .
