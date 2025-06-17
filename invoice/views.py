from django.template.loader import get_template
from django.http import HttpResponse, JsonResponse
from xhtml2pdf import pisa
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from order.models import ResolvedOrder
from userrole.models import Address
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_invoice_pdf(request, tracker):
    try:
        order = get_object_or_404(ResolvedOrder, tracker=tracker)
        # address = Address.objects.get(resolved_order=order)
        # print(address)
        if request.user != order.user or order.status == "AC":
            return Response({"error": "This invoice is not available for you or not paid"}, status=status.HTTP_403_FORBIDDEN)

        template = get_template("invoice_template.html")

        # Use hosted image link instead of file path
        logo_path = "https://res.cloudinary.com/dfac43kht/image/upload/v1748187173/logo-with-out-bg_n5akdk.png"

        # Format address fields
        address_text = "Address not available"
        try:
            print(f"Order address: {order.address}")  # Debug
            if order.address:
                print(f"Address fields: road={order.address.road}, city={order.address.city}")  # Debug
                address_parts = [
                    order.address.road,
                    order.address.city,
                    order.address.district,
                    order.address.post
                ]
                address_text = ", ".join(filter(None, address_parts))
                if not address_text.strip():
                    address_text = "Address not available"
        except Exception as e:
            print(f"Address error: {e}")  # Debug
            address_text = "Address not available"
        
        context = {
            "order": order,
            "logo_path": logo_path,
            "formatted_address": address_text
        }

        html = template.render(context)
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = f"attachment; filename=invoice_{order.tracker}.pdf"

        pisa_status = pisa.CreatePDF(html, dest=response)

        if pisa_status.err:
            return Response({"detail": "PDF generation failed."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return response

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)
