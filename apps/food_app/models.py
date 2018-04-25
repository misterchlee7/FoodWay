from __future__ import unicode_literals
from django.db import models
import re
import bcrypt
import datetime
# from django.contrib.auth.models import User

# Create your models here.
class UserManager(models.Manager):
    def register_validator(self, postData):
        # check all required fields
        errors = []

        first_name = postData['first_name']
        last_name = postData['last_name']
        email = postData['email'].lower()
        password = postData['password']
        confirm_password = postData['confirm_password']

        #first name
        if len(first_name) < 3:
            errors.append("First name must be at least 3 characters")
        if not first_name.isalpha():
            errors.append("First name cannot contain numbers or special characters")

        #last name
        if len(last_name) < 2:
            errors.append("Last name must be at least 2 characters")
        if not last_name.isalpha():
            errors.append("Last name cannot contain numbers or special characters")

        #email
        # check if email is taken or not
        filtered = self.filter(email=email)
        if not len(filtered) == 0:
            errors.append("Email is taken")

        EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9]+\.[a-zA-Z]+$')
        if len(email) == 0:
            errors.append("Email is required!")
        if not EMAIL_REGEX.match(email):
            errors.append("Invalid email address")

        #password
        if len(password) < 8:
            errors.append("Password must be at least 8 characters.")
        if password != confirm_password:
            errors.append("Passwords do not match")
            
        #phone number
        phone_regex = re.compile(r'^(\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}$')
        phone = postData['phone']
        if not phone_regex.match(phone):
            errors.append("Invalid phone number")
        if len(phone) == 0:
            errors.append("Phone number is required!")

        return errors

    def login_validator(self, postData):
        # check password with hashedpw
        # check if email/password fields
        errors = []
        email = postData['email'].lower()
        if len(email) == 0:
			errors.append("Email is required")
        if len(postData['password']) == 0:
			errors.append("Password is required")
        # matching email/password
        user = User.objects.filter(email=email).first()

        if user and bcrypt.checkpw(postData['password'].encode(), user.password.encode()):
            return {'user':user}
        else:
            errors.append('Email or password does not match')
            return {'errors':errors}

    def add_description(self,postData):
        user = User.objects.filter(id=postData['user_id'])
        return user.update(description=postData['description'])
    
    def validate_description(self, postData):
        errors = []
        if len(postData['description']) == 0:
            errors.append("Description is required!")
        return errors

    def create_user(self, postData):
        hashpw = bcrypt.hashpw(postData['password'].encode(), bcrypt.gensalt())
        if len(User.objects.all()) > 0:
            user_level = 1
        else:
            user_level = 9
        return User.objects.create(first_name = postData['first_name'],last_name = postData['last_name'], email = postData['email'].lower(), password = hashpw, phone=postData['phone'], user_level = int(user_level))
    
    def update_user(self, postData, user):
        # when its not description or nickname
        user.update()

    def delete_user(self, user):
        user.delete()


# adding/subtacting meal tickets
    def add_ticket(self, customer2):
        one_customer = customer2.first()
        meal_tix_left = one_customer.meal_tickets
        return customer2.update(meal_tickets = meal_tix_left + 1)
    
    def subtract_ticket(self, customer2):
        one_customer = customer2.first()
        meal_tix_left = one_customer.meal_tickets
        return customer2.update(meal_tickets = meal_tix_left - 1)

    def reload_basic(self, customer):
        customer1 = customer.first()
        meal_tix_left = customer1.meal_tickets
        return customer.update(meal_tickets = meal_tix_left + 10)

    def reload_premium(self, customer):
        customer1 = customer.first()
        meal_tix_left = customer1.meal_tickets
        return customer.update(meal_tickets = meal_tix_left + 15)

    def validate_ticket(self, postData):
        # maybe have the user's tickets# come through as postData
        errors = []
        user = User.objects.filter(id=postData['customer_id']).first()
        if user.meal_tickets == 0:
            errors.append("You don't have enough meal tickets! Please reload in Dashboard")
        return errors

class SubscriptionManager(models.Manager):
    def validate_subscription(self, postData):
        errors = []
        if len(postData['level']) == 0:
            errors.append('Please select either Basic or Premium Plan')
        return errors

    def subscribe(self, postData, customer):
        if postData['level'] == 1:
            cost = 120
            delivery_quantity = 10
            subscription_name = 'Basic'
        elif postData['level'] == 2:
            cost = 160
            delivery_quantity = 15
            subscription_name = 'Premium'
        
        customer = User.objects.filter(id=customer_id).first()
        return Subscription.objects.create(cost=cost, level=postData['level'], subscription_name=subscription_name, delivery_quantity=delivery_quantity, customer=customer)

class AddressManager(models.Manager):
    def validate_address(self, postData):
        errors = []
        street = postData['street']
        city = postData['city']
        state = postData['state']
        zipcode = postData['zipcode']
        if len(street) == 0:
            errors.append('Street is required!')
        if len(city) == 0:
            errors.append('city is required!')
        if len(state) == 0:
            errors.append('state is required!')
        if len(zipcode) == 0:
            errors.append('zipcode is required!')
        return errors

    def update_address(self, postData):
        errors = []
        street = postData['street']
        city = postData['city']
        state = postData['state']
        zipcode = postData['zipcode']
        if len(street) == 0:
            errors.append('Street is required!')
        if len(city) == 0:
            errors.append('city is required!')
        if len(state) == 0:
            errors.append('state is required!')
        if len(zipcode) == 0:
            errors.append('zipcode is required!')
        return errors
    
    def new_account_address(self, postData, user):
        return Address.objects.create(street=postData['street'], city=postData['city'], state=postData['state'], zipcode=postData['zipcode'], customer=user)

    def create_address(self, postData):
        user = User.objects.filter(id=postData['customer_id']).first()
        return Address.objects.create(street=postData['street'], city=postData['city'], state=postData['state'], zipcode=postData['zipcode'], customer=user)

class User(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    user_level = models.IntegerField()
    stripe_id = models.CharField(max_length=255, blank=True)
    meal_tickets = models.IntegerField(default = 0)
    created_at= models.DateTimeField(auto_now_add=True)
    updated_at= models.DateTimeField(auto_now=True)

    objects = UserManager()

class Address(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    zipcode = models.IntegerField()
    customer = models.ForeignKey(User, related_name="user_address")
    objects = AddressManager()
    
class Subscription(models.Model):
    cost = models.IntegerField()
    subscription_name = models.CharField(max_length=255)
    delivery_quantity = models.IntegerField()
    customer = models.ForeignKey(User, related_name='customer_subscription')
    objects = SubscriptionManager()

class DeliveryManager(models.Manager):
    def validate_delivery(self, postData):
        errors = []
    # validate date
        # datenow = datetime.datetime.strptime(postData['date'], '%Y-%m-%d')
        # if datetime.datetime.now() < datenow:
        #     errors.append('Date should be in the future')
        if len(postData['date']) == 0:
            errors.append('Date is required!')
    # time
        if len(postData['time']) == 0:
            errors.append('Time is required!')
    # validate details
        if len(postData['instructions']) == 0:
            errors.append('Please include delivery instructions')
    # validate restaurant
        if postData['restaurant'] == '':
            errors.append('Restaurant name is required')

        if postData['existing'] == "" and len(postData['street']) == 0:
            errors.append('Address is required')
        return errors

    def validate_update(self, postData):
        errors = []
    # validate date
        # datenow = datetime.datetime.strptime(postData['date'], '%Y-%m-%d')
        # if datetime.datetime.now() < datenow:
        #     errors.append('Date should be in the future')
        if len(postData['date']) == 0:
            errors.append('Date is required!')
    # time
        if len(postData['time']) == 0:
            errors.append('Time is required!')
    # validate details
        if len(postData['instructions']) == 0:
            errors.append('Please include delivery instructions')
        return errors

    def update_delivery(self, postData, delivery, address):
        return delivery.update(date = postData['date'], time=postData['time'], instructions=postData['instructions'], address=address)

    def create_delivery(self, postData, customer):
        # for address, in html form have the address show in dropdown and they can select, or add/create a new address?
        if len(postData['street']) < 1 and len(postData['city']) < 1:
            address = Address.objects.get(id= int(postData['existing']))
        else:
            address = Address.objects.create(street = postData['street'], city = postData['city'], state = postData['state'], zipcode = postData['zipcode'], customer=customer)

        return Delivery.objects.create(date = postData['date'], time=postData['time'], instructions=postData['instructions'], restaurant=postData['restaurant'], customer=customer, address=address)


    def cancel_the_delivery(self, delivery):
        delivery.delete()

class Delivery(models.Model):
    date = models.CharField(max_length=255)
    time = models.CharField(max_length=255)
    instructions = models.CharField(max_length=255)
    restaurant = models.CharField(max_length=255)
    address = models.ForeignKey(Address, related_name="delivery_address")
    customer = models.ForeignKey(User, related_name='customer_delivery')
    status = models.CharField(max_length=255, default="incomplete")
    created_at= models.DateTimeField(auto_now_add=True)
    updated_at= models.DateTimeField(auto_now=True)

    objects = DeliveryManager()

class Restaurant(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    cuisine = models.CharField(max_length=255)
    created_at= models.DateTimeField(auto_now_add=True)
    updated_at= models.DateTimeField(auto_now=True)

class RestaurantImage(models.Model):
    restaurant = models.OneToOneField(Restaurant, unique=True)
    image = models.ImageField(upload_to='images/')
    uploaded_at = models.DateField(auto_now_add=True)
