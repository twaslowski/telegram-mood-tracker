moved {
  from = module.dynamodb_table
  to   = module.user
}

module "user" {
  source = "terraform-aws-modules/dynamodb-table/aws"

  name     = "user"
  hash_key = "user_id"

  attributes = [
    {
      name = "user_id"
      type = "N"
    }
  ]

  billing_mode = "PAY_PER_REQUEST"
}

module "record" {
  source = "terraform-aws-modules/dynamodb-table/aws"

  name      = "record"
  hash_key  = "user_id"
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

  billing_mode = "PAY_PER_REQUEST"
}
