from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from .models import User, Contact


class UserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = '__all__'


class UserRegSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'type', 'password', 'password2']
        extra_kwargs = {'password': {'write_only': True}}

    def save(self, *args, **kwargs):
        user = User(email=self.validated_data['email'],
                    type=self.validated_data['type'])
        password = self.validated_data['password']
        password2 = self.validated_data['password2']

        if password != password2:
            raise serializers.ValidationError({'password error': 'passwords must match'})
        user.set_password(password)
        user.save()
        return user


class ContactSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Contact
        fields = ['id', 'city', 'street', 'house', 'structure', "building",
                  "apartment", "phone", "user"]
