from django.core.management.base import BaseCommand
from items.models import Item
from django.utils import timezone
import random

class Command(BaseCommand):
    help = 'Creates sample items with categories'

    def handle(self, *args, **kwargs):
        categories = ['Books', 'Electronics', 'Clothing', 'Home & Kitchen', 'Sports & Outdoors']
        
        items = [
            {
                'title': 'Django for Beginners',
                'description': 'A comprehensive guide to web development with Django.',
                'category': 'Books'
            },
            {
                'title': 'Python Cookbook',
                'description': 'Recipes for mastering Python 3',
                'category': 'Books'
            },
            {
                'title': 'Elasticsearch in Action',
                'description': 'Learn how to build scalable search applications using Elasticsearch',
                'category': 'Books'
            },
            {
                'title': 'Wireless Bluetooth Headphones',
                'description': 'High-quality sound with noise cancellation technology',
                'category': 'Electronics'
            },
            {
                'title': 'Smart LED TV 55"',
                'description': '4K Ultra HD resolution with smart features',
                'category': 'Electronics'
            },
            {
                'title': 'Men\'s Cotton T-Shirt',
                'description': 'Comfortable and breathable 100% cotton t-shirt',
                'category': 'Clothing'
            },
            {
                'title': 'Women\'s Running Shoes',
                'description': 'Lightweight and supportive shoes for runners',
                'category': 'Clothing'
            },
            {
                'title': 'Non-Stick Cookware Set',
                'description': '10-piece set of durable non-stick pots and pans',
                'category': 'Home & Kitchen'
            },
            {
                'title': 'Robot Vacuum Cleaner',
                'description': 'Smart navigation with app control for effortless cleaning',
                'category': 'Home & Kitchen'
            },
            {
                'title': 'Yoga Mat',
                'description': 'Extra thick and comfortable mat for yoga and exercise',
                'category': 'Sports & Outdoors'
            },
            {
                'title': 'Mountain Bike',
                'description': 'Durable 21-speed bike for off-road adventures',
                'category': 'Sports & Outdoors'
            },
            {
                'title': 'Portable Charger',
                'description': 'High-capacity power bank for charging devices on the go',
                'category': 'Electronics'
            },
            {
                'title': 'Stainless Steel Water Bottle',
                'description': 'Insulated bottle keeps drinks hot or cold for hours',
                'category': 'Sports & Outdoors'
            },
            {
                'title': 'Leather Wallet',
                'description': 'Slim and stylish wallet with RFID blocking',
                'category': 'Clothing'
            },
            {
                'title': 'Cast Iron Skillet',
                'description': 'Pre-seasoned skillet for versatile cooking',
                'category': 'Home & Kitchen'
            }
        ]

        # Clear existing items
        Item.objects.all().delete()

        for item_data in items:
            item = Item.objects.create(
                title=item_data['title'],
                description=item_data['description'],
                category=item_data['category'],
                created_at=timezone.now() - timezone.timedelta(days=random.randint(0, 365))
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully created item "{item.title}" in category "{item.category}"'))

        # Create some random items
        for i in range(35):  # Create 35 more random items
            category = random.choice(categories)
            item = Item.objects.create(
                title=f'Random Item {i+1}',
                description=f'This is a random item in the {category} category',
                category=category,
                created_at=timezone.now() - timezone.timedelta(days=random.randint(0, 365))
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully created random item "{item.title}" in category "{item.category}"'))

        self.stdout.write(self.style.SUCCESS('Sample items created successfully'))