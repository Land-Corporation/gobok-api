from rest_framework import serializers

from api.base.customer.models import Customer
from api.base.distributor_role.models import DistributorRole
from api.base.user.models import User
from api.versioned.v1.distributor.serializers import DistributorRoleSerializer
from common.choices import UserType
from common.serializer import CustomerSerializer


class UserInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'type', 'language',
                  'city', 'timezone', 'is_active')
        read_only_fields = ('email',)

    def to_representation(self, instance):
        assert hasattr(instance, 'type'), (
            f'Instance {self.__class__.__name__} missing "type" attribute')

        user_type = getattr(instance, 'type')

        if user_type == UserType.CUSTOMER:
            type_name = UserType(user_type).name.lower()
            try:
                cus_obj = Customer.objects.get(user=instance)
                customer = CustomerSerializer(cus_obj).data
                return self.serialize_customer_type(instance, type_name,
                                                    customer)
            except Customer.DoesNotExist:
                return self.serialize_customer_type(instance, type_name)

        if user_type == UserType.STAFF:
            type_name = UserType(user_type).name.lower()
            try:
                dist_role_obj = DistributorRole.objects.filter(user=instance)
                dist_roles = DistributorRoleSerializer(dist_role_obj,
                                                       many=True).data
                return self.serialize_staff_type(instance, type_name,
                                                 dist_roles)
            except DistributorRole.DoesNotExist:
                return self.serialize_staff_type(instance, type_name)

        raise TypeError(f'Instance {self.__class__.__name__} type({user_type}) '
                        f'does not match to any of UserType')

    def serialize_customer_type(self,
                                user: User,
                                type_name: str,
                                customer=None):
        dic = super().to_representation(user)
        dic['type'] = type_name
        if not customer:
            return dic

        dic['phone'] = customer.get('phone', None)
        dic['business_name'] = customer.get('business_name', None)
        return dic

    def serialize_staff_type(self, user: User, type_name: str, dist_roles=None):
        dic = super().to_representation(user)
        dic['type'] = type_name

        if not dist_roles:
            return dic

        dic['distributors'] = []
        dic['distributor_roles'] = []
        saved_dist = []
        for dist_role in dist_roles:
            dist_role.pop('user')
            dist = dist_role['distributor']
            dist_name = dist['name']

            if dist_name not in saved_dist:
                dic['distributors'].append(dist)
                saved_dist.append(dist_name)

            dic['distributor_roles'].append(dist_role)

        return dic
