import database

class PhotoSecurity:
    def __init__(self):
        pass

    @staticmethod
    def user_is_allowed_to_watch_photo(photo, user):
        if photo is None:
            return False
        if photo.privacy == 0:
            return True
        if user is None:
            return False
        if photo.owner.id() == user.key.id():  # Request user is owner
            return True
        else:
            if user.role_level > 2:  # Request user is admin
                return True
            else:
                if photo.privacy == 1:  # Photo is restricted
                    if user.role_level == 2:  # User account is activated by admin
                        permission = database.PhotoUserPermissionManager.get_user_photo_pair(photo, user)
                        if permission is not None:  # Owner has given permission to request user
                            return True
                        else:
                            return False
                    else:
                        return False
                else:
                    return False
