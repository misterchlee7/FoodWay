from django.shortcuts import render, redirect, reverse, HttpResponse
from .models import *
from django.contrib import messages
from django.http import HttpResponseRedirect
import stripe
from django.db.models import Count, Sum
from .forms import RestaurantForm
from django.contrib.auth import authenticate, login
from django.forms.forms import NON_FIELD_ERRORS
from django.conf import settings
from django.core.urlresolvers import reverse

stripe.api_key = settings.STRIPE_SECRET_KEY

# flash messages
def flash(request, errors, tag):
	for error in errors:
		messages.add_message(request, messages.ERROR, error, extra_tags=tag)
        
def index(request):
    return render(request, 'food_app/home.html')

def register(request):
    if not request.method == "POST":
        return redirect(reverse('landing'))
    else:
        registration_error = User.objects.register_validator(request.POST)
        address_error = Address.objects.validate_address(request.POST)

        if registration_error or address_error:
            flash(request, registration_error, "registration")
            flash(request, address_error, "registration")
        else:
            user = User.objects.create_user(request.POST)
            address = Address.objects.new_account_address(request.POST, user)
            request.session['user_id'] = user.id
            return redirect(reverse('dashboard'))
    return redirect(reverse('landing'))

def login(request):
    check = User.objects.login_validator(request.POST)
    for key in check:
        if key == 'user':
            request.session['user_id'] = check['user'].id
            if check['user'].user_level == 9:
                request.session['admin'] = True
            else:
                request.session['admin'] = False
            return redirect(reverse('dashboard'))
        else:
            flash(request, check['errors'], "login")
    return redirect(reverse('landing'))

def logout(request):
    request.session.flush()
    return redirect(reverse('landing'))

def user_delete(request, user_id):
    user = User.objects.filter(id=user_id).first()
    # only if user id == request.session['user_id']
    # OR if its admin
    if not user.id == request.session['user_id'] or not user.level == 9:
        return redirect(reverse('dashboard'))
    else:
        User.objects.delete_user(user)

def show_user(request, customer_id):
    # renders html to show user's profile
    user = User.objects.filter(id=customer_id).first()
    context = {
        'user': user,
        'subscriptions': user.customer_subscription.all()
    }
    return render(request, 'food_app/user.html', context)

def dashboard(request):
    if not 'user_id' in request.session:
        return redirect(reverse('landing'))
    else:
        user = User.objects.filter(id=request.session['user_id']).first()

        context = {
            'meal_tix': user.meal_tickets,
            'user': user, # load all user's delivery
            # user_deliveries: exclude the ones where status is complete
            'user_deliveries': user.customer_delivery.order_by('-id'),
            'count': user.customer_delivery.count(),
            # all the other restaurants they can purchase from
            'restaurants': Restaurant.objects.all()
        }
        return render(request, 'food_app/dash.html', context)

def new_subscription(request):
    return render(request, 'food_app/reload.html')

def make_subscription(request):
    if not request.method == "POST":
        return redirect(reverse('dashboard'))
    if not 'user_id' in request.session:
        return redirect(reverse('dashboard'))
    else:
        subscription_error = Subscription.objects.validate_subscription(request.POST)
        if subscription_error:
            flash(request, subscription_error, 'plan')
        else:
            customer = User.objects.filter(id=request.session['user_id']).first()
            Subscription.objects.subscribe(customer, request.POST)
            return redirect(reverse('dashboard'))
            
def basic_reload(request):
    customer = User.objects.filter(id=request.session['user_id'])
    User.objects.reload_basic(customer)
    return redirect(reverse('success'))

def premium_reload(request):
    customer = User.objects.filter(id=request.session['user_id'])
    User.objects.reload_premium(customer)
    return redirect(reverse('success'))

def cancel_delivery(request, delivery_id):
    # get delivery id and delete it, get subscription id to give one delivery_remain back
    the_delivery = Delivery.objects.filter(id=delivery_id).first()

    customer2 = User.objects.filter(id=request.session['user_id'])

    User.objects.add_ticket(customer2)
    Delivery.objects.cancel_the_delivery(the_delivery)
    return redirect(reverse('dashboard'))

def update_delivery(request, delivery_id):
    update_error = Delivery.objects.validate_update(request.POST)
    if update_error:
        flash(request, update_error, 'update')
        return redirect(reverse('update', kwargs={"delivery_id": delivery_id}))
    else: 
        delivery = Delivery.objects.filter(id=delivery_id)
        customer = User.objects.filter(id=request.POST['customer_id']).first()
        spec_delivery = Delivery.objects.filter(id=delivery_id).first()

        #  if no new address was added
        if len(request.POST['street']) == 0:
            address_picked = request.POST['existing']
            Delivery.objects.update_delivery(request.POST, delivery, address_picked)
        # if new thing was added, check for address validation if no errors, create
        else:
            addy_error = Address.objects.update_address(request.POST)
            if addy_error:
                flash(request, addy_error, "update")
                return redirect(reverse('update', kwargs={"delivery_id": spec_delivery.id}))
            else:
                # no error, create new address
                address = Address.objects.create_address(request.POST)
                Delivery.objects.update_delivery(request.POST, delivery, address)
        return redirect(reverse('dashboard'))

def new_delivery(request):
    # get customer with customer_id, get latest subscription and update meal tix
    if request.method != "POST":
        return redirect(reverse('dashboard'))
    else:
        delivery_error = Delivery.objects.validate_delivery(request.POST)
        tix_error = User.objects.validate_ticket(request.POST)
        if tix_error or delivery_error:
            flash(request, tix_error, 'tickets')
            flash(request, delivery_error, 'delivery')
            return redirect(reverse('add'))
        else:
            customer = User.objects.filter(id=request.POST['customer_id']).first()
            customer2 = User.objects.filter(id=request.POST['customer_id'])
            
            Delivery.objects.create_delivery(request.POST, customer)
            User.objects.subtract_ticket(customer2)

            return redirect(reverse('dashboard'))

def add(request):
    # form to add new delivery
    # validate form
    user = User.objects.filter(id=request.session['user_id']).first()

    user_addresses = Address.objects.filter(customer = user).all()

    context = {
        "addresses": [],
    }
    for address in user_addresses:
        context['addresses'].append(address)
    return render(request, 'food_app/add.html', context)

def update(request, delivery_id):
    user = User.objects.filter(id=request.session['user_id']).first()
    delivery = user.customer_delivery.get(id = delivery_id)

    user_addresses = Address.objects.filter(customer = user).all()

    context = {
        "deliveries": delivery,
        "addresses": [],
    }
    for address in user_addresses:
        context['addresses'].append(address)

    return render(request, 'food_app/update.html', context)

def reload_wallet(request):
    return render(request, 'food_app/reload.html')
# payment STRIPE
def process_basic(request):
    the_customer = User.objects.get(id = request.session['user_id'])
    if request.method == "POST":
        token = request.POST.get("stripeToken")
    try:
        charge = stripe.Charge.create(
            amount = 12000,
            currency = "usd",
            source = token, 
            description = "Premium package was charged to the customer"
        )
        the_customer.stripe_id = charge.id
    except stripe.error.CardError as ce:
        return False, ce
    else:
        Subscription.objects.create(cost=120, subscription_name="Basic", delivery_quantity="10", customer=the_customer)
        the_customer.save()
        return redirect(reverse('basic_reload'))

def process_premium(request):
    the_customer = User.objects.get(id = request.session['user_id'])
    if request.method == "POST":
        token = request.POST.get("stripeToken")
    try:
        charge = stripe.Charge.create(
            amount = 16000,
            currency = "usd",
            source = token, 
            description = "Premium package was charged to the customer"
        )
        the_customer.stripe_id = charge.id
    except stripe.error.CardError as ce:
        return False, ce
    else:
        Subscription.objects.create(cost=160, subscription_name="Premium", delivery_quantity="15", customer=the_customer)
        the_customer.save()
        return redirect(reverse('premium_reload'))

def success(request):
    return render(request, 'food_app/success.html')

# Admin Login Portal Page
def admin_portal(request):
    request.session["admin"] = False
    return render(request, "food_app/admin_portal.html")

# Admin Login Portal Process
def admin_portal_proc(request):
    user = User.objects.filter(email=request.POST["admin_email"]).first()
    if user:
        if user.user_level == 9 and bcrypt.checkpw(request.POST["admin_pw"].encode(), user.password.encode()):
            request.session["admin"] = True
            return redirect(reverse('admin_dash_orders'))
    errors = {}
    errors["admin_log"] = "Email or Password is invalid"
    for key, error in errors.iteritems():
        messages.error(request, error)
    return redirect(reverse('admin_portal'))

# Admin Timed Redirect Page (5 sec)
def admin_redirect(request):
    return render(request,"food_app/admin_redirect.html")

# Admin Dashboard - Order Page
def admin_dash_orders(request):
    if request.session["admin"] == False:
        return redirect(reverse('dashboard'))
    else:
        context = {
            "deliveries" : Delivery.objects.all(),
        }
        return render(request, "food_app/admin_dash.html", context)

# Admin Dashboard - Restaurants Page
def admin_dash_res(request):
    if request.session["admin"] == False:
        return redirect(admin_redirect)
    else:
        context = {
            "food_places" : Restaurant.objects.all(),
        }
        return render(request, "food_app/admin_products.html", context)

# Admin Dashboard - Subscribers Page
def admin_dash_sub(request):
    if request.session["admin"] == False:
        return redirect(admin_redirect)
    
    all_customers = User.objects.all()
    obj = []
    total_money = 0
    for customer in all_customers:
        total_earned = 0
        for payment in customer.customer_subscription.all():
            total_earned += payment.cost
            total_money += payment.cost
        obj.append({"customer":customer, "total":total_earned})
    else:
        context = {
            "sub" : customer,
            "obj": obj,
            "total_earned" : total_money,
            "count" : Subscription.objects.all().values("cost").count(),
            "unique_users" : len(Subscription.objects.values("customer__first_name").distinct()),
        }
        return render(request, "food_app/admin_subs.html", context)

# Admin Add/Edit Subscriber Page
def admin_update_sub(request, user_id):
    if request.session["admin"] == False:
        return redirect(admin_redirect)
    else:
        user = User.objects.filter(id=user_id).first()
        context = {
            "user" : User.objects.filter(id=user_id).first(),
            "address": Address.objects.filter(customer__id=user_id).first()
        }
    return render(request, "food_app/admin_edit_sub.html", context)

# Admin update the Subscriber process
def admin_update_sub_proc(request, user_id):
    user = User.objects.filter(id=user_id).first()
    address = Address.objects.filter(customer=user).first()
    user.first_name=request.POST["first_name"]
    user.last_name=request.POST["last_name"]
    user.email=request.POST["email"]
    user.phone=request.POST["phone"]
    # HASH this before launch
    # user.password=request.POST["password"]
    user.user_level=request.POST["user_level"]
    address.street=request.POST["street"]
    address.city=request.POST["city"]
    address.state=request.POST["state"]
    address.zipcode=request.POST["zipcode"]
    user.meal_tickets=request.POST["meal_tickets"]
    user.save()
    return redirect(reverse("admin_dash_sub"))

# Admin Add/Edit Restaurant Page
def admin_edit_place(request, res_id):
    form = RestaurantForm(use_required_attribute=False)
    if request.session["admin"] == False:
        return redirect(admin_redirect)
    else:
        if res_id == "98631":
            context = {
                "res_name" : "",
                "res_id" : res_id,
            }
        else:
            context = {
                "res" : Restaurant.objects.filter(id=res_id).first(),
                "res_id" : res_id,
                'form': form,
            }
        return render(request, "food_app/admin_edit_product.html", context)

# Admin update the restaurant process
def admin_update_place(request, res_id):
    res = Restaurant.objects.filter(id=res_id).first()
    if request.method == 'POST':
        if len(request.FILES) > 0:
            form = RestaurantForm(request.POST, request.FILES)
            if form.is_valid():
                # form.save()
                if len(RestaurantImage.objects.filter(restaurant = res)) == 0:
                    resImage = RestaurantImage.objects.create(restaurant = res, image = request.FILES['image'])
                    resImage.save()
                else:
                    resImage = RestaurantImage.objects.get(restaurant = res)
                    resImage.image = request.FILES['image']
                    resImage.save()
        res.name=request.POST["res_name"]
        res.description=request.POST["description"]
        res.cuisine=request.POST["cuisine"]
        res.save()
        return redirect(reverse("admin_add_place"))

# Admin add a new restaurant process
def admin_add_new(request):
    Restaurant.objects.create(name=request.POST["res_name"], description=request.POST["description"],cuisine=request.POST["cuisine"])
    return redirect(reverse("admin_add_place"))

# Admin delete restaurant process
def admin_del_place(request, res_id):
    res = Restaurant.objects.filter(id=res_id).first()
    res.delete()
    return redirect(reverse("admin_add_place"))

def admin_del_user(request, user_id):
    user = User.objects.filter(id=user_id).first()
    user.delete()
    return redirect(reverse('admin_dash_sub'))