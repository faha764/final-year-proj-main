from django.contrib.auth.tokens import PasswordResetTokenGenerator


admin_token_generator = PasswordResetTokenGenerator()

from django.contrib.auth.tokens import PasswordResetTokenGenerator

class SellerTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, seller, timestamp):
       
        return str(seller.pk) + str(seller.password) + str(timestamp)

seller_token_generator = SellerTokenGenerator()

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.crypto import salted_hmac
from django.utils.http import int_to_base36, base36_to_int
from datetime import datetime

class CustomTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
       
        return f"{user.pk}{timestamp}{user.password}"

customer_token_generator = CustomTokenGenerator()


from django.contrib.auth.tokens import PasswordResetTokenGenerator

class SellerTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, seller, timestamp):
        
        return str(seller.pk) + str(timestamp) + str(seller.password)

seller_token_generator = SellerTokenGenerator()

  


