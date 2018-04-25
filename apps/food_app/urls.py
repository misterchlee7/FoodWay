from django.conf.urls import url
from . import views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns= [
    url(r'^$', views.index, name="landing"), # has form for login reg
    url(r'^register', views.register, name="register"), 
    url(r'^login', views.login, name="login"),
    url(r'^logout', views.logout, name="logout"),
    url(r'^dashboard$', views.dashboard, name="dashboard"), 
    url(r'^plan/subscribe', views.make_subscription, name="make_subscription"),
#form to create new subscr
    url(r'^subscription/new', views.new_subscription, name="new_subscription"),
# handles request to reload basic level
    url(r'^user/reload_basic', views.basic_reload, name="basic_reload"),
# handles request to reload premium
    url(r'^user/reload_premium', views.premium_reload, name="premium_reload"),
# handle request to update delivery
    url(r'^user/delivery/update/(?P<delivery_id>\d+)', views.update_delivery, name="update_delivery"),
# form to update delivery (template)
    url(r'^user/delivery/update_form/(?P<delivery_id>\d+)', views.update, name="update"),
# route for cancelling delivery
    url(r'^user/delivery/cancel/(?P<delivery_id>\d+)', views.cancel_delivery, name="cancel_delivery"),
# template for payment plan options
    url(r'user/reload_wallet', views.reload_wallet, name="reload_wallet"),
    # processing payments:
    url(r'^user/process/basic', views.process_basic, name="process_basic"),
    url(r'^user/process/premium', views.process_premium, name="process_premium"),
    # success page (template) after payment
    url(r'^user/purchase/success', views.success, name="success"),


# just the form template for new delivery
    url(r'^plan/add$', views.add, name="add"),
# handle post to create new delivery
    url(r'^user/delivery/new', views.new_delivery, name="new_delivery"),

# show user profile
    url(r'^user/(?P<customer_id>\d+)', views.show_user, name="show_user"),



# ADMIN login portal page
    url(r'^admin/$', views.admin_portal, name="admin_portal"),

# ADMIN login portal process
    url(r'^admin/process$', views.admin_portal_proc),

# ADMIN redirect page (5 sec timer)
    url(r'^admin/redirect$', views.admin_redirect, name="redirect"),

# ADMIN dashboard orders page
    url(r'^admin/dashboard$', views.admin_dash_orders, name="admin_dash_orders"),

# ADMIN dashboard restaurants page
    url(r'^admin/dashboard/add_place$', views.admin_dash_res, name="admin_add_place"),

# ADMIN dashboard subscribers page
    url(r'^admin/dashboard/subscribers$', views.admin_dash_sub, name="admin_dash_sub"),

# ADMIN edit subscribers page
    url(r'^admin/dashboard/subscribers/edit/(?P<user_id>\d+)$', views.admin_update_sub, name="admin_update_sub"),
# ADMIN edit subscribers process
    url(r'^admin/dashboard/subscribers/process/(?P<user_id>\d+)$', views.admin_update_sub_proc, name="admin_update_sub"),
# ADMIN edit restaurants page
    url(r'^admin/dashboard/edit/(?P<res_id>\d+)$', views.admin_edit_place, name="admin_edit_place"),

# ADMIN update restaurant process
    url(r'^admin/dashboard/update/(?P<res_id>\d+)$', views.admin_update_place, name="admin_update_place"),

# ADMIN add a new restaurant process
    url(r'^admin/dashboard/add$', views.admin_add_new, name="admin_add_new"),

# ADMIN delete the restaurant process
    url(r'^admin/dashboard/delete/(?P<res_id>\d+)$', views.admin_del_place, name="admin_del_place"),

    url(r'^admin/dashboard/subscribers/delete/(?P<user_id>\d+)', views.admin_del_user),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# (?P<subscription_id>\d+)/
