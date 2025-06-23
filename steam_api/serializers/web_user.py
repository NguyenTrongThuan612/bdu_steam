import re
from rest_framework import serializers
from steam_api.models.web_user import WebUser, WebUserRole

class WebUserSerializer(serializers.ModelSerializer):
    class Meta: 
        model = WebUser
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        existing = set(self.fields.keys())
        fields = kwargs.pop("fields", []) or existing
        exclude = kwargs.pop("exclude", [])
        
        super().__init__(*args, **kwargs)
        
        for field in exclude + list(set(existing) - set(fields)):
            self.fields.pop(field, None)

class CreateWebUserSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    phone = serializers.CharField(required=False)
    password = serializers.CharField(required=True)
    role = serializers.ChoiceField(choices=WebUserRole.choices, required=True)

    def validate_phone_number(self, value):
        phone_pattern = re.compile(r"^(?:\+)?[0-9]{6,14}$")
        if not phone_pattern.match(value):
            raise serializers.ValidationError("Invalid phone number!")
        
        return value
    
    def validate_password(self, value):
        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&_-])[A-Za-z\d@$!%_#*?&-]{8,30}$', value):
            raise serializers.ValidationError("Mật khẩu không hợp lệ. Yêu cầu ít nhất 8 ký tự, bao gồm chữ cái viết thường, viết hoa, số và ký tự đặc biệt.")
        
        return value
    
    def validate_role(self, value):
        if value == WebUserRole.ROOT:
            raise serializers.ValidationError("Không thể tạo tài khoản với quyền ROOT!")
        return value

class VerifyWebUserSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(required=True)