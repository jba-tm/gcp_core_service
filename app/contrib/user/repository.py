from app.db.repository import CRUDBase

from .models import User, Group, UserToGroup


class CRUDUser(CRUDBase[User]):
    pass


class CRUDGroup(CRUDBase[Group]):
    pass


class CRUDUserToGroup(CRUDBase[UserToGroup]):
    pass


user_repo = CRUDUser(User)
group_repo = CRUDGroup(Group)
user_to_group_repo = CRUDUserToGroup(UserToGroup)
