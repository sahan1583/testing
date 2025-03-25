from django.shortcuts import render
from django.http import JsonResponse
from .models import ChatMessage
from django.views.decorators.csrf import csrf_exempt
import json

# Fetch the last 5 messages (on chat open)
def fetch_messages(request):
    messages = ChatMessage.objects.order_by('-timestamp')[:5]
    messages_data = [
        {
            "id": msg.id,
            "image": msg.image.url if msg.image else None,
            "location": msg.location,
            "title": msg.title,
            "description": msg.description,
            "timestamp": msg.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        }
        for msg in messages
    ]
    return JsonResponse({"messages": messages_data})


# Fetch older messages for infinite scrolling
def load_more_messages(request):
    last_msg_id = request.GET.get('last_id')
    messages = ChatMessage.objects.filter(id__lt=last_msg_id).order_by('-timestamp')[:5]

    messages_data = [
        {
            "id": msg.id,
            "image": msg.image.url if msg.image else None,
            "location": msg.location,
            "title": msg.title,
            "description": msg.description,
            "timestamp": msg.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        }
        for msg in messages
    ]
    return JsonResponse({"messages": messages_data})


# Save a new message
@csrf_exempt
def save_message(request):
    if request.method == "POST":
        data = request.POST
        image = request.FILES.get("image")  # Handle image file

        chat_message = ChatMessage.objects.create(
            location=data.get("location", ""),
            title=data["title"],
            description=data["description"],
            image=image
        )
        return JsonResponse({"success": True, "message": "Message saved!"})

@csrf_exempt
def send_message(request):
    if request.method == "POST":
        data = json.loads(request.body)
        message = data.get("message", "")

        # Replace with actual response logic
        bot_response = f"I received: {message}"

        return JsonResponse({"response": bot_response})

    return JsonResponse({"error": "Invalid request"}, status=400)