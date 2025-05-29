from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from resend import Emails
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from rest_framework.response import Response
# Create your views here.

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def contact(request):
    title = request.data.get('title', '')
    description = request.data.get('description', '')
    image = request.FILES.get('image', None)

    if not title or not description:
        return Response({"detail": "Title and description are required."}, status=400)

    image_html = f'<img src="{image.url}" alt="Image">' if image else ''

    Emails.send({
        "from": "America to BD <noreply@americatobd.com>",
        "to": ["support@americatobd.com"],
        "subject": "User Support - America to BD",
        "html": f"""
        <h2>{title}</h2>
        {image_html}
        <p>{description}</p>
        <p>User: <strong>{request.user.email}</strong> | Phone: <strong>{request.user.userinfo.phone}</strong></p>
        """
    })

    return Response({"detail": "Support request sent successfully."})