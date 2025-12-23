from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminOrReadOnly(BasePermission):
    """
    Anyone can GET/HEAD/OPTIONS.
    Only staff can POST/PUT/PATCH/DELETE.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)

class IsDriver(BasePermission):
    """
    Driver = authenticated Account that has a related Driver row via OneToOne.
    Expected related_name: driver_profile OR driver (adjust below if needed).
    """
    driver_attr = "driver_profile"  # change to "driver" if your related_name is 'driver'

    def has_permission(self, request, view):
        u = request.user
        return bool(u and u.is_authenticated and hasattr(u, self.driver_attr))

class IsCustomer(BasePermission):
    """
    Customer = authenticated Account that is NOT a driver.
    """
    driver_attr = "driver_profile"  # change to "driver" if your related_name is 'driver'

    def has_permission(self, request, view):
        u = request.user
        return bool(u and u.is_authenticated and not hasattr(u, self.driver_attr))