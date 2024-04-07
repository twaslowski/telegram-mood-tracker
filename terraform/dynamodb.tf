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
