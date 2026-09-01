from django.urls import path
from . import views
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

from django.conf import settings


urlpatterns = [
   
    #welcome
    path("", views.welcome, name="welcome"),

    #chat
    path("customer/<int:product_id>/<int:seller_id>/", views.chat_room_customer, name="chat_room_customer"),
    path("seller/<int:product_id>/<int:customer_id>/", views.chat_room_seller, name="chat_room_seller"),
    path("send/<int:room_id>/", views.send_message, name="send_message"),
    path("customer/chats/", views.customer_chat_list, name="customer_chat_list"),
    path("seller/chats/", views.seller_chat_list, name="seller_chat_list"),
    path("chat/<int:room_id>/messages/", views.get_messages, name="get_messages"),
    path('chat/<int:seller_id>/', views.chatbox, name='chatbox'),
    path("customer/chat-list-refresh/", views.refresh_chat_list_customer, name="refresh_chat_list_customer"),
    path("seller/chat-list-refresh/", views.refresh_chat_list_seller, name="refresh_chat_list_seller"),
    path("get_messages/<int:room_id>/", views.get_messages, name="get_messages"),
    path('chat/<int:product_id>/', views.chatbox, name='chatbox'),

    #reviews
    path('reviewsrating/', views.reviews_rating_view, name='reviewsrating'),
    path('api/send-reply/', views.send_reply_api, name='send_reply_api'),
    path('submit-product-review/<int:item_id>/', views.submit_product_review, name='submit_product_review'),

    #order
    path('retry-payment/<int:order_id>/', views.retry_payment, name='retry_payment'),
    path('api/seller/orders/', views.seller_orders_api, name='seller_orders_api'),
    path('api/seller/orders/<int:order_id>/details/', views.seller_order_detail_api, name='seller_order_detail_api'),
    path('api/seller/orders/<int:order_id>/update_status/', views.seller_update_order_status, name='seller-update-order-status'),

    #user management
    path('admindashboard/', views.admindashboard, name='admindashboard'),
    path('usermanagement/', views.usermanagement, name='usermanagement'),
    path('toggle_seller_status/<int:seller_id>/', views.toggle_seller_status, name='toggle_seller_status'),
    path('toggle_customer_status/<int:customer_id>/', views.toggle_customer_status, name='toggle_customer_status'),
    path("check-unique/", views.check_unique, name="check_unique"), 
    path('sellerprofilee/<int:seller_id>/', views.seller_profile_by_admin, name='sellerprofilee'),
    
    #admin order payment
    path('sellerpayout/', views.sellerpayout, name='sellerpayout'),
    path('send-payout/<int:order_id>/', views.send_payout, name='send_payout'),
    path('orderpayment/', views.orderpayment, name='orderpayment'),
    
    #seller redirect from home
    path("seller/redirect/", views.seller_redirect, name="seller_redirect"),

    #category
    path('category/<int:cat_id>/', views.category_products, name='category_products'),
    path("admindashboard/category/<int:category_id>/products/", views.admin_category_products, name="admin_category_products"),
    path('admincategory/', views.admincategory, name='admincategory'),
    path('delete-category/<int:cat_id>/', views.delete_category, name='delete_category'),
    path('delete-category/<int:category_id>/', views.delete_category, name='delete_category'),
    path('categories/edit/<int:cat_id>/', views.edit_category, name='edit_category'),

    #cust order
    path('myorders/', views.myorders, name='myorders'),
    path('orders/cancel/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('cancel-order/<int:order_id>/', views.cancel_order_ajax, name='cancel_order_ajax'),
    path('order-details/<int:order_id>/', views.order_details_ajax, name='order_details_ajax'),
    path('dashboard/orders/', views.admin_order_payments, name='orderpayment'),
    path('dashboard/orders/<int:order_id>/<str:action>/', views.update_order_status, name='update_order_status'),
    
    #admin login
    path('adminlogin/', views.adminlogin, name='adminlogin'),
    
    #seller dashboard
    path('seldashboardok/', views.seldashboardok, name='seldashboardok'),

    #seller order and product management
    path('manageorder/', views.manageorder, name='manageorder'),
    path('manproductok/', views.manproductok, name='manproductok'),
    path('addproduct/', views.addproduct, name='addproduct'),
    path('edit-product/<int:product_id>/', views.editproduct, name='editproduct'), 
    path('deleteproduct/<int:product_id>/', views.delete_product, name='deleteproduct'),
    
    #seller profile
    path('seller/profile/<int:seller_id>/', views.view_seller_profile, name='view_seller_profile'),
    path('seller/<int:seller_id>/', views.view_seller_prof, name='view_seller_prof'),
    path('editprofile/', views.editprofile, name='editprofile'),
    path('sellerprofilee/', views.sellerprofilee, name='sellerprofilee'),

    path('seller/earnings/', views.seller_earnings, name='seller_earnings'),

   
    #seller help centre
    path('selfaqs/', views.selfaqs, name='selfaqs'),

    #cust registration
    path('custsignup/', views.custsignup_view, name='custsignup'),
    path('custlogin/', views.custlogin, name='custlogin'),
    path('customerlogout/', views.customer_logout, name='customerlogout'),
    path('customerdashboard/', views.customerdashboard, name='customerdashboard'),

    #seller registration
    path('sellersignup/', views.sellersignup_view, name='sellersignup'),
    path('sellerlogin/', views.sellerlogin, name='sellerlogin'),
    path('sellerlogout/', views.sellerlogout, name='sellerlogout'),
    path('createprofile/', views.createprofile, name='createprofile'),
    path('forgetpassword/', views.forgetpassword, name='forgetpassword'),

    #trending and featured products
    path('trendingproducts/', views.trendingproducts, name='trendingproducts'),
    path('featuredproducts/', views.featuredproducts, name='featuredproducts'),

    #prod detail page
    path("product/<int:product_id>/", views.productdetail, name="productdetail"),

    #cart
    path('cart_vie/', views.cart_vie, name='cart_vie'),
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('remove_from_cart_ajax/<int:item_id>/', views.remove_from_cart_ajax, name='remove_from_cart_ajax'),
    path('update_cart_quantity/', views.update_cart_quantity, name='update_cart_quantity'),
    path('delete_all_cart_items/', views.delete_all_cart_items, name='delete_all_cart_items'),

    #checkout and payment
    path('checkout/', views.checkout, name='checkout'),
    path('save-shipping/', views.save_shipping_detail, name='save_shipping'),
    path('selectpayment/', views.selectpayment, name='selectpayment'),
    path('paymentconfirmss/', views.paymentconfirmss, name='paymentconfirmss'),
    path('paymentconfirms/', views.payment_confirms_view, name='paymentconfirms'),
    
    #customer terms and policies
    path('aboutuss/', views.aboutuss, name='aboutuss'),  
    path('contactus/', views.contactus, name='contactus'),
    path('helpcenter/', views.helpcenter, name='helpcenter'),
    path('termcondition/', views.termcondition, name='termcondition'),
    path('custterms/', views.custterms, name='custterms'),
    path('refund/', views.refund, name='refund'),
    path('exchange/', views.exchange, name='exchange'),
    path('privacypolicy/', views.privacypolicy, name='privacypolicy'),
    path('termsandconditions/', views.termsandconditions, name='termsandconditions'),

    #wishlist
    path('wishlist/', views.wishlistok, name='wishlistok'),
    path('wishlist/add/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:item_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlist/remove_ajax/<int:item_id>/', views.remove_from_wishlist_ajax, name='remove_from_wishlist_ajax'),

    #home
    path('homeee/', views.homeee, name='homeee'),  

    #notification
    path('notification/<str:role>/', views.notification, name='notification'),
    path('notification/mark-read/<int:id>/<str:role>/', views.mark_notification_read, name='mark_notification_read'),
    path("adminlogin/", views.adminlogin, name="adminlogin"),
    path("admindashboard/", views.admindashboard, name="admindashboard"),
    path('search/', views.search_products, name='search_products'),

    #admin forget password
    path('admin-forgot-password/', views.admin_forgot_password, name='admin_forgot_password'),
    path('admin-reset-password/<uidb64>/<token>/', views.admin_reset_password, name='admin_reset_password'),
    path('admin-reset-confirm/', views.admin_reset_confirm, name='admin_reset_confirm'),
    path("admin-reset/<uidb64>/<token>/", views.admin_reset_confirm, name="admin_reset_confirm"),
    path('admin/reset-password/<uid>/<token>/', views.admin_reset_password, name='admin_reset_password'),
    path('admin-forgot-password/', views.admin_forgot_password, name='admin_forgot_password'),
    path('admin-reset-password-email/<uid>/<token>/', views.admin_reset_password, name='admin_reset_password'),
    path("admin-forgot-password/", views.admin_forgot_password, name="admin_forgot_password"),
    path("admin-reset-password/<uidb64>/<token>/", views.admin_reset_password, name="admin_reset_password"),
    path('Adminlogin/', views.Adminlogin, name='Adminlogin'),
    path('Adminlogout/', views.Adminlogout, name='Adminlogout'), 
    
    path('admindashboard/', views.admindashboard, name='admindashboard'),

    #seller forget password
    path("seller-forgot-password/", views.seller_forgot_password, name="seller_forgot_password"),
   
    #customer forget password
    path('forgot-password/', views.customer_forgot_password, name='customer_forgot_password'),
    path('forgot-password-done/', views.customer_forgot_password_done, name='customer_forgot_password_done'),
    path('customer-reset-password/<uidb64>/<token>/', views.customer_reset_password, name='customer_reset_password'),
    path('forgot-password/', views.customer_forgot_password, name='customer_forgot_password'),
    path('forgot-password-done/', views.customer_forgot_password_done, name='customer_forgot_password_done'),
    path('customer-reset-password/<uidb64>/<token>/', views.customer_reset_password, name='customer_reset_password'),
    path("customer-forgot-password/", views.customer_forgot_password, name="customer_forgot_password"),
    path("customer-reset-password/<uidb64>/<token>/", views.customer_reset_password, name="customer_reset_password"),
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name="password_reset_form.html",
        email_template_name="password_reset_email.html",
        subject_template_name="password_reset_subject.txt",
        success_url="/password-reset/done/"
    ), name="password_reset"),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name="password_reset_done.html"
    ), name="password_reset_done"),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name="password_reset_confirm.html",
        success_url="/reset/complete/"
    ), name="password_reset_confirm"),
    path('reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name="password_reset_complete.html"
    ), name="password_reset_complete"),


    path("forgot-password/", views.customer_forgot_password, name="customer_forgot_password"),
    path("password-reset-done/", views.customer_password_reset_done, name="customer_password_reset_done"),
    path("customer-reset-password/<uidb64>/<token>/", views.customer_reset_password, name="customer_reset_password"),
    path('customer-forgot-password-done/', views.customer_forgot_password_done, name='forgot_password_done'),
    path("password-reset-done/", views.customer_password_reset_done, name="customer_password_reset_done"),
    path('forgot-password-done/', views.customer_forgot_password_done, name='customer_forgot_password_done'),
    path('adminnotification/', views.adminnotification, name='adminnotification'),

    path('sellnotification/', views.sellnotification, name='sellnotification'),

    path(
        "seller-reset/<uidb64>/<token>/",
        views.seller_reset_password,  
        name="seller_reset_confirm"
    ),
    path('sellerlogin/', views.sellerlogin, name='sellerlogin'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
