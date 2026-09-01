from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from django.utils import timezone
from django.utils.timezone import now
from datetime import timedelta
from django.contrib.auth.hashers import make_password, check_password 

#seller table

class Seller(models.Model):
    name = models.CharField(max_length=25)
    email = models.EmailField(unique=True, null=True, blank=True)
    contact = models.CharField(max_length=20, null=True, blank=True)

    shop_name = models.CharField(max_length=25, null=False)
    cnic = models.CharField(max_length=15, unique=True)
    account_type = models.CharField(max_length=20, null=True, blank=True)
    account_number = models.CharField(max_length=20)
    account_holder_name = models.CharField(max_length=100, null=True, blank=True)
    password = models.CharField(max_length=100)

   
    full_name = models.CharField(max_length=100, null=True, blank=True)
    username = models.CharField(max_length=100, unique=True, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    experience = models.IntegerField(null=True, blank=True)
    skills = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    profile_image = models.ImageField(upload_to='seller_profiles/', null=True, blank=True)
    additional_details = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, default='Active') 

   
    last_login = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return self.name



#contact us table

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} - {self.subject}"

    
#customer table

class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, null=True, blank=True)
    contact = models.CharField(max_length=11, null=True, blank=True)
    password = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=100, default='Active') 

    def __str__(self):
        return self.name

    
#catogory table

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return self.name

#product table

class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=0)
    quantity = models.PositiveIntegerField()
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    customized = models.BooleanField(default=False)
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)

    is_trending = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    def __str__(self):
        return self.name
    
#order table

class Order(models.Model):
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status_updated_at = models.DateTimeField(auto_now=True)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_method = models.CharField(max_length=50, default='unknown')
    payment_screenshot = models.ImageField(upload_to='payment_screenshots/', null=True, blank=True)
    seller = models.ForeignKey(Seller, on_delete=models.SET_NULL, null=True, blank=True)

    commission_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    seller_earning = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    
    payout_status = models.CharField(max_length=20, choices=[
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
    ], default='Pending')

    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    
    created_at = models.DateTimeField(default=now)
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('cancelled', 'Cancelled'),
        ('delivered', 'Delivered'),      
         
    ]

    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='pending')
    def seller_gets(self):
       return round(self.seller_earning, 2)

    def __str__(self):
        return f"Order #{self.id} by {self.customer.name} - {self.status}"
    def is_cancelable(self):
       
        time_diff = timezone.now() - self.created_at
        return self.status in ['pending','Confirmed'] and time_diff < timedelta(hours=24)
    
    def calculate_commission(self, percentage=10):
        self.commission_amount = (self.total_amount * Decimal(percentage)) / Decimal('100')
        self.seller_earning = (self.total_amount * (Decimal('100') - Decimal(percentage)) / Decimal('100')) + self.shipping_fee
        self.save()


#orderitem table

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    delivered_date = models.DateField(null=True, blank=True)

    
   
    image_url = models.URLField()

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"
    
   
#product review table

class ProductReview(models.Model):
    order_item = models.OneToOneField(
        OrderItem,
        related_name='review',
        on_delete=models.CASCADE
    )
    customer = models.ForeignKey(
        Customer,  
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    review_text = models.TextField()
    rating = models.PositiveSmallIntegerField(default=5)
    image = models.ImageField(upload_to='review_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    seller_reply = models.TextField(blank=True, null=True)
    reply_date = models.DateTimeField(blank=True, null=True)

    

    def __str__(self):
        return f"Review for {self.order_item.product_name}"

#customer shipping detail table

class ShippingDetail(models.Model):
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    full_name = models.CharField(max_length=100)
    address = models.TextField()
    city = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Shipping for {self.customer.name} to {self.city}"

#wishlist table

class WishlistItem(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)  
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer} - {self.product.name}"

#cartitem table

class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def total_price(self):
        return self.product.price * self.quantity
    def save(self, *args, **kwargs):
       
        if self.quantity > self.product.quantity:
            self.quantity = self.product.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.customer.name} - {self.product.name}"

#notification table

class Notification(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('seller', 'Seller'),
        ('customer', 'Customer'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    target_id = models.IntegerField(null=True, blank=True)  
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.role} - {self.message[:30]}"

#admin table

class Admin(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100) 
    status = models.CharField(max_length=20, default='Active')

    def __str__(self):
        return self.email

    class Meta:
        db_table = 'main_admin'   
        managed = False           
    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self.save()

  
    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

#chatroom table

class ChatRoom(models.Model):
    customer = models.ForeignKey(Customer, related_name="customer_chats", on_delete=models.CASCADE)
    seller = models.ForeignKey(Seller, related_name="seller_chats", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('customer', 'seller', 'product')  

    def __str__(self):
        return f"Chat: {self.customer.name} ↔ {self.seller.name} ({self.product.name})"

# chat message table
class Message(models.Model):
    room = models.ForeignKey(ChatRoom, related_name="messages", on_delete=models.CASCADE)
    sender_type = models.CharField(max_length=10, choices=[("customer", "Customer"), ("seller", "Seller")])
    sender_id = models.IntegerField(null=True, blank=True)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)  

    class Meta:
        ordering = ['timestamp']
