from rest_framework import permissions

from api.models.room.models import Room


class IsRoomOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.

    Note that the permission-checks for objects are done by DRF in the method
    APIView.check_object_permissions. So if you use this permission in viewset
    other than APIView, need to manually call `has_object_permission`.
    """

    def has_object_permission(self, request, view, obj: Room) -> bool:
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Instance must have an attribute named `user`.
        return obj.user == request.user
