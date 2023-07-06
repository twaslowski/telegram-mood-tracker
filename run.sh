# run persistence backend
docker ps --format '{{.Names}}' | grep -q mood-tracker-mongo
if [ "$?" -eq 0 ]; then
  echo "mongodb is already running"
else
  docker run -d -p 27017:27017 --name mood-tracker-mongo mongo:latest
fi

ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
export PYTHONPATH=$PYTHONPATH:$ROOT_DIR

# Install dependencies
source venv/bin/activate
pip install -r requirements.txt

python src/app.py
