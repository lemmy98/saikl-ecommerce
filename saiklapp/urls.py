from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings




from .views import *

urlpatterns = [
    path('register/', registerPage, name="register"),
    path('login/', loginPage, name="login"),
    path('logout/', logoutUser, name="logout"),

    path('', home, name='home'),
    path('store/', store, name="store"),
    path('cart/', cart, name="cart"),
    path('checkout/', checkout, name="checkout"),
    path('admindash/', admindash, name="admindash"),
    path('checkout/', checkout, name="checkout"),
     path('user/',usersettings,name='usersettings'),
    path('products/',products,name='products'),
    path('customer/<str:pk>',customer, name='customer'),
    path('feedback/', feedback, name='feedback'),
    path('thanks/', thanks, name='thanks'),


    path('addproduct/',addproduct,name='addproduct'),
    path('updateproduct/<str:pk>',updateproduct,name='updateproduct'),
    path('product_details/<str:pk>',productdetail,name='product_details'),
    path('update_order/<str:pk>/', updateOrder, name="update_order"),
    path('delete_order/<str:pk>/', deleteOrder, name="delete_order"),

    

    path('update_item/', updateItem, name="update_item"),
    path('process_order/', processOrder, name="process_order"),

    path('forgot-password/', PasswordForgotView.as_view(template_name='store/forgotpassword.html'), name="passwordforgot"),
    path('password-reset/<email>/<token>/', passwordResetView.as_view(template_name='store/passwordreset.html'), name = "passwordreset"),


]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)