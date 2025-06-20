# import os
# import django

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "americatobd.settings")  # replace with your project name
# django.setup()

# from django.db import connection

# with connection.cursor() as cursor:
#     cursor.execute("SELECT * FROM customer")
#     rows = cursor.fetchall()
#     for row in rows:
#         print(row)
#     print(len(row))

import json

with open('customer.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("Number of customers:", len(data))
