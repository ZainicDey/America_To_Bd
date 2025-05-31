from rest_framework import generics, status, viewsets, response

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from . import serializers

from resend import Emails

class PasswordReset(generics.GenericAPIView):
    """
    Request for Password Reset Link.
    """

    serializer_class = serializers.EmailSerializer

    def post(self, request):
        """
        Create token.
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data["email"]
        user = User.objects.filter(email=email).first()
        if user:
            encoded_pk = urlsafe_base64_encode(force_bytes(user.pk))
            token = PasswordResetTokenGenerator().make_token(user)
            reset_url = reverse(
                "reset-password",
                kwargs={"encoded_pk": encoded_pk, "token": token},
            )
            print(reset_url)
            reset_link = f"{settings.FRONTEND_URL}{reset_url}"

            # send the rest_link as mail to the user.

            Emails.send({
                "from": "America to BD <noreply@americatobd.com>",
                "to": [user.email],
                "subject": "Password Reset - America to BD",
                "html": f"""
                <h2>Password Reset Request</h2>
                <p>Dear {user.first_name} {user.last_name},</p>
                <p>Click the link below to reset your password:</p>
                <p><a href="{reset_link}">{reset_link}</a></p>
                <p>If you didn't request this password reset, please ignore this email.</p>
                """
            })
            
            return response.Response(
                {
                    "message": "Password reset link has been sent to your email"
                },
                status=status.HTTP_200_OK,
            )
        else:
            return response.Response(
                {"message": "User doesn't exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ResetPasswordAPI(generics.GenericAPIView):
    """
    Verify and Reset Password Token View.
    """

    serializer_class = serializers.ResetPasswordSerializer

    def patch(self, request, *args, **kwargs):
        """
        Verify token & encoded_pk and then reset the password.
        """
        serializer = self.serializer_class(
            data=request.data, context={"kwargs": kwargs}
        )
        serializer.is_valid(raise_exception=True)
        return response.Response(
            {"message": "Password reset complete"},
            status=status.HTTP_200_OK,
        )