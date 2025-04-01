from django.contrib.auth.models import User, AnonymousUser, AbstractBaseUser
from .models import UserProfile
from typing import cast

# Type stubs to tell the type checker about userprofile attributes
User.userprofile: UserProfile  # type: ignore
AnonymousUser.userprofile: None  # type: ignore

# Type assertion for authenticated users
def get_authenticated_user(user: AbstractBaseUser | AnonymousUser) -> User:
    assert user.is_authenticated
    return cast(User, user) 