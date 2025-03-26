from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from .models import ChatMessage
import json

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import ChatMessage
from .serializers import ChatMessageSerializer



class ChatMessageListCreateView(APIView):
    def get(self, request):
        """Fetch paginated chat messages"""
        page = int(request.GET.get("page", 1))
        messages = ChatMessage.objects.all().order_by("-created_at")[(page-1)*5: page*5]
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """Send a new chat message"""
        serializer = ChatMessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from .models import ChatMessage

@csrf_exempt
def chat_messages(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))  # ✅ Parse JSON correctly
            title = data.get("title", "").strip()
            description = data.get("description", "").strip()
            location = data.get("location", "").strip()

            if not title or not description or not location:
                return JsonResponse({"error": "All fields are required"}, status=400)

            new_message = ChatMessage.objects.create(title=title, description=description, location=location)

            return JsonResponse({
                "title": new_message.title,
                "description": new_message.description,
                "location": new_message.location,
                "created_at": new_message.created_at.strftime("%Y-%m-%d %H:%M:%S")
            }, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)

    return JsonResponse({"error": "Invalid request"}, status=400)
