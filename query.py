import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "americatobd.settings")
django.setup()

from userrole.models import UserModel
from django.contrib.auth.models import User
import json

with open('customer.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

new_id = {}

for customer in data:
    # Skip if user with this email already exists
    if User.objects.filter(email=customer['email']).exists():
        continue
    # Skip if user model with this phone already exists
    phone = customer['phone'].lstrip('+')
    if UserModel.objects.filter(phone=phone).exists():
        continue

    user = User.objects.create_user(
        username=customer['email'],
        password="123",
        email=customer['email'],
        first_name=customer['first_name'],
        last_name=customer['last_name']
    )
    user_model = UserModel.objects.create(
        user=user,
        phone=phone
    )
    new_id[customer['id']] = user_model.id

with open('new_id_map.json', 'w', encoding='utf-8') as f:
    json.dump(new_id, f, ensure_ascii=False, indent=4)
