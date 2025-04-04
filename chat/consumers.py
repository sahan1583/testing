import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import ChatMessage
from asgiref.sync import sync_to_async
from django.core.exceptions import ObjectDoesNotExist 

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
        """Handle messages sent by users or requests for older messages"""
        data = json.loads(text_data)
        message_type = data.get("type")

        if message_type == "load_older_messages":
            oldest_message_id = data.get("oldest_id")
            older_messages = await self.get_older_messages(oldest_message_id, count=15)
            # Send older messages back *only* to the requesting client
            await self.send(text_data=json.dumps({"type": "older_chat_history", "messages": older_messages}))

        elif message_type == "chat_message": # Assume default is sending a message if type isn't specified or is 'chat_message'
            title = data.get("title")
            description = data.get("description")
            location = data.get("location")
            image_url = data.get("image", None) # Use get for safety

            if not all([title, description, location]): # Basic validation
                    # Optionally send an error back to the user
                    # await self.send(text_data=json.dumps({"type": "error", "message": "Missing required fields."}))
                    return # Don't process incomplete messages

            message = await self.save_message(title, description, location, image_url)

            # Broadcast the new message to all users in the group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message_broadcast", # Use a different type for broadcasting
                    **message # Expand message dict
                }
            )

    async def chat_message_broadcast(self, event):
        """Send broadcast messages (new chat messages) to WebSocket clients"""
        # The 'type' key here is internal for Channels routing;
        # we repackage it for the client.
        await self.send(text_data=json.dumps({
            "type": "chat_message", # This is the type the client JS expects
            "title": event["title"],
            "description": event["description"],
            "location": event["location"],
            "created_at": event["created_at"],
            "image": event["image"],
            "id": event["id"] # Include message ID
        }))

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

    @staticmethod
    def _serialize_messages(messages):
        """Helper to serialize a list of message objects."""
        serialized = []
        for msg in messages:
             # Prepare image URL for sending
            image_url = None
            if msg.image:
                 try:
                    if hasattr(msg.image, 'url'):
                         image_url = msg.image.url
                         if image_url.startswith("/media/media/"):
                             image_url = image_url.replace("/media/media/", "/media/", 1)
                 except ValueError:
                     image_url = None

            serialized.append({
                "id": msg.id, # Include message ID
                "title": msg.title,
                "description": msg.description,
                "location": msg.location,
                "created_at": msg.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "image": image_url,
            })
        return serialized

    @sync_to_async
    def get_last_messages(self, count=15):
        """ Fetch the most recent 'count' messages from the database """
        messages = ChatMessage.objects.order_by("-created_at")[:count]
        # Messages are fetched newest first, reverse to show oldest of the batch first
        return self._serialize_messages(reversed(messages))


    @sync_to_async
    def get_older_messages(self, oldest_id=None, count=15):
        """Fetch 'count' messages older than the message with oldest_id."""
        if oldest_id is None:
             # Should not happen if called correctly from frontend, but handle defensively
            return []

        try:
            # Get the timestamp of the oldest message currently shown
            oldest_message = ChatMessage.objects.get(pk=oldest_id)
            # Fetch messages created *before* that one
            messages = ChatMessage.objects.filter(
                created_at__lt=oldest_message.created_at
            ).order_by("-created_at")[:count] # Fetch newest among the older ones
            # Reverse to maintain chronological order for prepending
            return self._serialize_messages(reversed(messages))
        except ObjectDoesNotExist:
             # If the oldest_id doesn't exist for some reason, return empty
            return []
