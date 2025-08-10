from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from register.models import registermodel,Car,Booking


class registrationserializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = registermodel
        fields = ['Email', 'Name', 'Mobile_no', 'Date_Of_Birth', 'password', 'password2']
        extra_kwargs = {'password': {'write_only': True}}
    def validate(self,attrs):
         password=attrs.get('password')
         password2=attrs.get('password2')
         if password != password2:
             raise serializers.ValidationError('Password and confirm Password Must Be Same',)
         return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        password2 = validated_data.pop('password2')
        if password != password2:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        user = registermodel(**validated_data)
        user.set_password(password)
        user.save()
        return user 
    
class loginserializer(serializers.ModelSerializer):
    Email=serializers.EmailField(max_length=100)
    class Meta:
        model=registermodel
        fields=['Email','password']

class userprofileserializer(serializers.ModelSerializer):
    class Meta:
        model=registermodel
        fields=['Email','Name','Date_Of_Birth','Mobile_no']

class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = ['id', 'car_name', 'is_booked','city','image','available_from']

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['id', 'car', 'pickup_date', 'pickup_time', 'dropoff_date', 'dropoff_time']
        read_only_fields = ['user']
    def validate(self, data):
        required_files = ['driving_licence', 'residence_proof', 'pan_card', 'aadhaar_card', 'payment_screenshot']
        missing = [field for field in required_files if not data.get(field)]

        if missing:
            raise serializers.ValidationError(f"The following documents are required: {', '.join(missing)}")
        return data

User = get_user_model()

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    confirm_password = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "New passwords do not match."})
        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user