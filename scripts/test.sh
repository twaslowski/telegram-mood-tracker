echo "launching localstack container"
docker run -d --rm --name localstack -p 4566:4566 -p 4571:4571 localstack/localstack

echo "waiting for localstack to be ready"
sleep 3

echo "creating user dynamodb table ..."
aws dynamodb create-table --table-name user \
  --attribute-definitions AttributeName=user_id,AttributeType=N \
  --key-schema AttributeName=user_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --endpoint-url http://localhost:4566 > /dev/null

echo "creating record dynamodb table ..."
aws dynamodb create-table --table-name record \
  --attribute-definitions AttributeName=timestamp,AttributeType=S \
  --attribute-definitions AttributeName=user_id,AttributeType=N \
  --key-schema AttributeName=timestamp,KeyType=RANGE \
  --key-schema AttributeName=user_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --endpoint-url http://localhost:4566 > /dev/null

echo "cleaning up"
# docker stop localstack
