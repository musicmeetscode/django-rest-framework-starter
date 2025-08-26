# from django.core.exceptions import ValidationError
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
# from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework.response import Response
from rest_framework import status, generics, views
from accounts.models import CustomUser
from main import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode


from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate

from .serializers import LoginRequestSerializer, RegisterSerializer, EmailVerificationSerializer, LoginSerializer, \
    ResetPasswordWithEmailSerializer, SetNewPasswordSerializer, PasswordTokenCheckSerializer, MeAPIViewSerializer, UserDataSerialiser, UserWithTokenSerializer, \
    UsersSerializer
from .utils import Util
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import permissions
from services.rederers import Renderer
from services import customPermission


class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    renderer_classes = (Renderer,)

    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        user_data = serializer.data

        user = CustomUser.objects.get(email=user_data['email'])
        # token = RefreshToken.for_user(user).access_token

        relative_link = reverse('verify-email')
        current_site = get_current_site(request).domain

        abs_url = f"http://{current_site}{relative_link}?token="

        email_body = 'Hi {} Use below link to verify your email \n {}'.format(
            user.full_name, abs_url)
        data = {'to_email': CustomUser.email, 'email_body': email_body,
                'email_subject': 'Verify your email'}
        Util.send_email(data)

        return Response(user_data, status=status.HTTP_201_CREATED)


class VerifyEmail(APIView):
    serializer_class = EmailVerificationSerializer
    renderer_classes = (Renderer,)

    token_param_config = openapi.Parameter(
        'token', in_=openapi.IN_QUERY, description='Description', type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self, request):
        token = request.GET.get('token')
        try:
            # payload = jwt.decode(token, settings.SECRET_KEY)
            user = CustomUser.objects.get(id=payload['user_id'])
            if not CustomUser.is_verified:
                CustomUser.is_verified = True
                CustomUser.save()
            return Response({'email': 'Successfully Verified'}, status=status.HTTP_201_CREATED)
        except:
            return Response({'email': 'Invalid Token'}, status=status.HTTP_400_BAD_REQUEST)


class LoginApiView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    renderer_classes = (Renderer,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ResetPasswordWithEmail(generics.GenericAPIView):
    serializer_class = ResetPasswordWithEmailSerializer
    renderer_classes = (Renderer,)

    def post(self, request):
        data = {'request': request, 'data': request.data}
        serializer = self.serializer_class(data=data)
        email = request.data['email']

        if CustomUser.objects.filter(email=email).exists():
            user = CustomUser.objects.get(email=email)

            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = get_current_site(request=request).domain

            relative_link = reverse(
                'password-reset-confirm', kwargs={'uidb64': uidb64, 'token': token})
            abs_url = 'http://' + current_site + relative_link

            email_body = 'Hi, \n Use below link to reset your password \n {}'.format(
                abs_url)
            data = {'to_email': CustomUser.email, 'email_body': email_body,
                    'email_subject': 'Reset your password'}
            Util.send_email(data)

            return Response({'success': 'We have send you a link to reset your password'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'not found email'}, status=status.HTTP_406_NOT_ACCEPTABLE)


class PasswordTokenCheckAPI(generics.GenericAPIView):
    serializer_class = PasswordTokenCheckSerializer
    renderer_classes = (Renderer,)

    def get(self, request, uidb64, token):
        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({'error': 'Token is not valid, please request a new one'}, status.HTTP_401_UNAUTHORIZED)

            return Response({'success': True, 'message': 'Credential valid', 'uidb64': uidb64, 'token': token}, status=status.HTTP_200_OK)
        except DjangoUnicodeDecodeError as err:
            return Response({'error': 'Token is not valid, please request a new one'}, status.HTTP_401_UNAUTHORIZED)


class SetNewPasswordAPIView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer
    renderer_classes = (Renderer,)

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'success': True, 'message': 'Password reset success'}, status=status.HTTP_200_OK)


class UserListAPIView(generics.ListCreateAPIView):
    serializer_class = UsersSerializer
    queryset = CustomUser.objects.all()
    renderer_classes = (Renderer,)
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        return serializer.save()

    def get_queryset(self):
        return self.queryset


class UserDetailsAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UsersSerializer
    queryset = CustomUser.objects.all()
    renderer_classes = (Renderer,)
    permission_classes = (permissions.IsAuthenticated,
                          customPermission.IsUsersPermission)
    lookup_field = 'id'

    def get_queryset(self):
        return self.queryset


class MeAPIView(views.APIView):
    serializer_class = MeAPIViewSerializer
    renderer_classes = (Renderer,)
    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request):
        user_info = CustomUser.objects.get(id=request.user.id)
        serializer = self.serializer_class(user_info)

        return Response(serializer.data, status=status.HTTP_200_OK)


class LoginViewSet(APIView):
    permission_classes = []

    @swagger_auto_schema(
        request_body=LoginRequestSerializer,
        operation_summary="Authenticate and login a user",
        operation_description="To login users,pass a JSON Object with their email and password(For social accounts, pass their IDTOKEN)",
        responses={200: UserWithTokenSerializer, 400: "Bad request"},)
    def post(self, request, format=None):
        result = {"error": False, }
        status_res = status.HTTP_200_OK
        user = authenticate(
            request=request,
            email=request.data.get("email"),
            password=request.data.get("password")
        )
        if user is None:
            raise ValidationError({'error': 'Incorrect credentials'})
        else:
            if user.deleted:
                CustomUser.objects.filter(
                    id=request.user.id).update(deleted=False)
            result['user'] = UserDataSerialiser(user, many=False).data
            result['user']['token'] = Token.objects.get_or_create(user=user)[
                0].key
        return Response(data=result, status=status_res, content_type="application/json")
