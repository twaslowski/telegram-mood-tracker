import src.repository.user_repository as user_repository


def migrate_notifications():
    """
    The data structure for metrics and notifications has changed.
    This function migrates the data to the new structure by simply deleting the old user data structure
    and replacing it with the new one. Every user was simply using the defaults anyhow, so no data is lost.
    :return:
    """
    for user in user_repository.user.find():
        user_repository.user.delete_one({"user_id": user["user_id"]})
        user_repository.create_user(user["user_id"])


if __name__ == "__main__":
    migrate_notifications()
