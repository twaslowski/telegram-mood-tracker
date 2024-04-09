module "dynamodb_table" {
  source   = "terraform-aws-modules/dynamodb-table/aws"

  name     = "user"
  hash_key = "user_id"

  attributes = [
    {
      name = "user_id"
      type = "N"
    }
  ]
}

module "dynamodb_table" {
  source   = "terraform-aws-modules/dynamodb-table/aws"

  name     = "record"
  hash_key = "user_id"
  range_key = "timestamp"

  attributes = [
    {
      name = "user_id"
      type = "N"
    },
    {
      name = "timestamp"
      type = "S"
    }
  ]

}
