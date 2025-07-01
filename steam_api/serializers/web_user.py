import re
from rest_framework import serializers
from steam_api.models.web_user import WebUser, WebUserRole, WebUserStatus, WebUserGender

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

class UpdateWebUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebUser
        fields = ['staff_id', 'name', 'birth_date', 'gender', 'email', 'phone', 'status']
        extra_kwargs = {
            'staff_id': {'required': False},
            'name': {'required': False},
            'birth_date': {'required': False},
            'gender': {'required': False},
            'email': {'required': False},
            'phone': {'required': False},
            'status': {'required': False}
        }

    def validate_phone(self, value):
        phone_pattern = re.compile(r"^(?:\+)?[0-9]{6,14}$")
        if not phone_pattern.match(value):
            raise serializers.ValidationError("Invalid phone number!")
        return value

    def validate(self, data):
        request = self.context.get('request')
        if not request or not request.user:
            raise serializers.ValidationError("Authentication required")

        user_allowed_fields = {'name', 'birth_date', 'gender', 'phone'}
        admin_only_fields = {'staff_id', 'email', 'status'}

        attempted_fields = set(data.keys())

        if request.user.role == WebUserRole.ROOT:
            invalid_fields = attempted_fields - admin_only_fields
            if invalid_fields:
                raise serializers.ValidationError(
                    f"Admin chỉ được phép sửa các trường: {', '.join(admin_only_fields)}"
                )
        else:
            if request.user.id != self.instance.id:
                raise serializers.ValidationError("Bạn chỉ có thể sửa thông tin của chính mình")

            invalid_fields = attempted_fields - user_allowed_fields
            if invalid_fields:
                raise serializers.ValidationError(
                    f"Bạn chỉ được phép sửa các trường: {', '.join(user_allowed_fields)}"
                )

        if 'status' in data and request.user.id == self.instance.id:
            raise serializers.ValidationError("Không thể thay đổi trạng thái của chính mình")

        return data