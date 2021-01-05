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


class IsRoomPropOwnerOrReadyOnly(permissions.BasePermission):
    """
    If the user in incoming request owns room, then this user can has
    permission to perform job on room's properties such as images.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Permissions are only allowed to the owner of the room.
        if type(obj) is Room:
            return obj.user == request.user
        return obj.room.user == request.user
