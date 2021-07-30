from django.contrib.admin import ModelAdmin
from django.contrib import admin
from .models import *


# Register your models here.
class CustomerAdmin(admin.ModelAdmin):
    list_display = ( 'name', 'email', 'phone',)
    list_filter = ('user',)
    search_fields = ( 'email',)

    class Meta:
        model = Customer

class FeedbackAdmin(admin.ModelAdmin):
    list_display = ( 'name', 'email', 'subject', 'date', 'happy',)
    list_filter = ('date',)
    search_fields = ('message',)

    class Meta:
        model = Feedback

admin.site.register(Customer, CustomerAdmin)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ShippingAddress)
admin.site.register(Feedback, FeedbackAdmin)