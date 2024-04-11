from rest_framework import serializers as s

from users.models import Avatar, Profile


class AvatarSerializer(s.ModelSerializer):
    src = s.SerializerMethodField()

    class Meta:
        model = Avatar
        fields = ["src", "alt"]

    def get_src(self, obj) -> str:
        return obj.src.url


class ProfileSerializer(s.ModelSerializer):
    avatar = AvatarSerializer(allow_null=True)

    class Meta:
        model = Profile
        fields = ('fullName', 'email', 'phone', 'avatar')

    def update(self, instance: Profile, validated_data) -> Profile:

        instance.fullName = validated_data.get('fullName', instance.fullName)
        instance.email = validated_data.get('email', instance.email)
        instance.phone = validated_data.get('phone', instance.phone)
        if not validated_data.get('avatar'):
            instance.avatar = None
        instance.save()
        return instance
