echo "launching localstack container"
docker run -d --rm --name localstack -p 4566:4566 -p 4571:4571 localstack/localstack

echo "waiting for localstack to be ready"
sleep 3

echo "running tests"
if [ -d .venv ]; then
  echo "found existing virtual environment. activating ..."
  source .venv/bin/activate
else
  echo "no virtual environment found. assuming dependencies are available."
fi

export PYTHONPATH=./ && poetry run pytest test/ --ignore test/integration/manual/ --disable-warnings -s -v

echo "cleaning up"
docker stop localstack
