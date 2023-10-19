from app.db.repository import CRUDBase

from .models import School, UserToSchool


class CRUDSchool(CRUDBase[School]):
    pass


class CRUDUserToSchool(CRUDBase[UserToSchool]):
    pass


school_repo = CRUDSchool(School)
user_to_school_repo = CRUDUserToSchool(UserToSchool)
