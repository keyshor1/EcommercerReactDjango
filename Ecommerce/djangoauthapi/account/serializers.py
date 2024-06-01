from rest_framework import serializers
from account.models import User
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from account.utils import Util

class UserRegistrationSerializer(serializers.ModelSerializer):
    # we are writin to conform password 2 in registration request
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    class Meta:
        model= User
        fields= ['email', 'name', 'tc', 'password', 'password2']
        extra_kwargs= {
            'password': {'write_only': True}
        }

    # receiving and validating password and confirm password while registration
    # this validate funtion run when is_valid get execute in view.py
    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        if password != password2:
            raise serializers.ValidationError('password and confirm password doesnot match')
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
    
class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=200)
    class Meta:
        model = User
        fields = ["email", "password"]

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "name", "email"]

class UserChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=250, style={'input_type': 'password'}, write_only=True)
    password2 = serializers.CharField(max_length=250, style={'input_type': 'password'}, write_only=True)
    
    class Meta:
        fields = ['password', 'password2']
    
    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        # get the user using context dictionay
        user = self.context.get('user')
        if password != password2:
            raise serializers.ValidationError("password and confirm password didnot match")
        user.set_password(password)
        user.save()
        return attrs
    
class SendPasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    
    class Meta:
        fields = ['email']

    def validate(self, attrs):
        email = attrs.get('email')
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email = email)
            # makes uid innencode and convert the uid to byte inorder to incode 
            uid = urlsafe_base64_encode(force_bytes(user.id))
            print("uid", uid)
            token = PasswordResetTokenGenerator().make_token(user)
            print("token", token)
            link = 'http://localhost:3000/api/user/reset/'+ uid + '/' + token
            print('passwordresetlink:', link)
            # send mail
            body = 'Click here to reset your password ' + link
            data={
                'subject':'Passsword Reset',
                'body': body,
                'to_email': user.email
            }
            Util.send_email(data)
            return attrs
        else:
            raise serializers.ValidationError('you are not registered')
        

class UserPasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=250, style={'input_type': 'password'}, write_only=True)
    password2 = serializers.CharField(max_length=250, style={'input_type': 'password'}, write_only=True)
    
    class Meta:
        fields = ['password', 'password2']
    
    def validate(self, attrs):
        try:
            password = attrs.get('password')
            password2 = attrs.get('password2')
            # get the token and uid using context dictionay
            uid = self.context.get('uid')
            token = self.context.get('token')
            if password != password2:
                raise serializers.ValidationError("password and confirm password didnot match")
            # decode uid to string
            id = smart_str(urlsafe_base64_decode(uid))
            user = User.objects.get(id=id)
            # check the user token match with email token or not with help of passwordresttokengenerator function
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise serializers.ValidationError("Token is not valid or expired")

            user.set_password(password)
            user.save()
            return attrs
        except DjangoUnicodeDecodeError as identifier:
            PasswordResetTokenGenerator().check_token(user, token)
            raise serializers.ValidationError("Token is not valid or expired")
