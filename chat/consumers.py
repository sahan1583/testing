import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import ChatMessage
from .serializers import ChatMessageSerializer
from asgiref.sync import sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Handle new WebSocket connections"""
        self.room_name = "chat_room"
        self.room_group_name = f"chat_{self.room_name}"

        # ✅ Join the WebSocket group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # ✅ Fetch last 10 messages and send them to the user
        last_messages = await self.get_last_messages()
        for msg in last_messages:
            await self.send(text_data=json.dumps(msg))

    async def disconnect(self, close_code):
        """Handle disconnection"""
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """Handle messages sent by users"""
        data = json.loads(text_data)
        title = data["title"]
        description = data["description"]
        location = data["location"]
        image = data.get("image", None)  # Handle optional image

        # ✅ Save message to the database
        message = await self.save_message(title, description, location, image)

        # ✅ Send the message to all users in the chat room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "title": title,
                "description": description,
                "location": location,
                "created_at": message.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "image": message.image.url if message.image else None,
            }
        )

    async def chat_message(self, event):
        """Send messages to WebSocket clients"""
        await self.send(text_data=json.dumps(event))

    @sync_to_async
    def save_message(self, title, description, location, image):
        """ Save the message to the database in a synchronous function """
        return ChatMessage.objects.create(
            title=title, description=description, location=location, image=image
        )
    
    @sync_to_async
    def get_last_messages(self):
        """ Fetch the last 10 messages from the database """
        messages = ChatMessage.objects.order_by("-created_at")[:10]  # Fetch latest 10
        messages = reversed(messages)  # Reverse order to send oldest first
        return [
            {
                "title": msg.title,
                "description": msg.description,
                "location": msg.location,
                "created_at": msg.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "image": msg.image.url if msg.image else None,
            }
            for msg in messages
        ]