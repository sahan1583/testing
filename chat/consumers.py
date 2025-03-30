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

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # Fetch last 10 messages and send them as a batch
        last_messages = await self.get_last_messages()
        await self.send(text_data=json.dumps({"type": "chat_history", "messages": last_messages}))

    async def disconnect(self, close_code):
        """Handle disconnection"""
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """Handle messages sent by users"""
        data = json.loads(text_data)

        if data.get("type") == "load_history":  
            last_messages = await self.get_last_messages()
            await self.send(text_data=json.dumps({"type": "chat_history", "messages": last_messages}))

        else:
            title = data["title"]
            description = data["description"]
            location = data["location"]
            image_url = data.get("image", None)

            message = await self.save_message(title, description, location, image_url)

            #  Immediately send the message to the sender
            # await self.send(text_data=json.dumps({
            #     "type": "chat_message",
            #     **message  # Expand message dict
            # }))

            #  Broadcast to all users
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    **message
                }
            )

    async def chat_message(self, event):
        """Send messages to WebSocket clients"""
        await self.send(text_data=json.dumps(event))

    @sync_to_async
    def save_message(self, title, description, location, image_url):
        """ Save the message to the database """
        message = ChatMessage.objects.create(
            title=title,
            description=description,
            location=location,
            image=image_url
        )
        image_url = None
        if message.image:
            image_url = message.image.url
            if image_url.startswith("/media/media/"):
                image_url = image_url.replace("/media/media/", "/media/")  

        return {
            "title": message.title,
            "description": message.description,
            "location": message.location,
            "created_at": message.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "image": image_url,
        }

    @sync_to_async
    def get_last_messages(self):
        """ Fetch the last 10 messages from the database """
        messages = ChatMessage.objects.order_by("-created_at")[:10]  
        messages = reversed(messages)  
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
