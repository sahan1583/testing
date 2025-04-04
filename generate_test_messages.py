import os
import django
import random
from faker import Faker
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

# ✅ Setup Django settings BEFORE importing models
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "animalwellness.settings")  # Replace `your_project` with your actual project name
django.setup()  # Initialize Django

# Now import models after setting up Django
from chat.models import ChatMessage

# Fake Data Generator
fake = Faker()

# Generate 40 test messages
for _ in range(40):
    title = fake.sentence(nb_words=6)
    description = fake.text(max_nb_chars=100)
    location = fake.city()

    # Create a test image (optional)
    image_path = None
    if random.choice([True, False]):  # Randomly decide whether to add an image
        image_data = fake.image(size=(200, 200))  # Generate fake image bytes
        file_name = f"chat_images/{fake.file_name(category='image')}"
        saved_path = default_storage.save(file_name, ContentFile(image_data))
        image_path = saved_path  # Store file path in DB

    # Create the message in DB
    ChatMessage.objects.create(title=title, description=description, location=location, image=image_path)

print("✅ 40 Test Messages Created Successfully!")
