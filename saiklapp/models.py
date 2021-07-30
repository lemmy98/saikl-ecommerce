from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete= models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200, null=True)
    email = models.EmailField(max_length=200, null=True)
    phone = models.CharField(max_length=200, null=True)
    profile_pic = models.ImageField(default='default.png', null=True, blank = True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)

    
    def __str__(self):
        return self.name
        # return '{} for email {}'.format(self.name, self.email)

    @property
    def image_url(self):
     if self.profile_pic and hasattr(self.profile_pic, 'url'):
        return self.profile_pic.url
    
class Product(models.Model):
    name = models.CharField(max_length=200, null=True)
    price = models.DecimalField(max_digits=9, decimal_places=3)
    category = models.CharField(max_length=200, null=True)
    digital = models.BooleanField(default=False, null=True, blank=False)
    description = models.CharField(max_length=200, null=True, blank=True)
    image = models.ImageField(null=True, blank=True)

    def __str__(self):
         return self.name

    @property
    def imageURL(self):
            try:
                url = self.image.url
            except:
                url = ''
            return url





class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True)
    product = models.ForeignKey(Product, null=True, on_delete=models.SET_NULL)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False, null=True,blank=True)
    transaction_id = models.CharField(max_length=200, null=True)


    def __str__(self):
        # return str(self.customer)
        return '{} placed order on {}'.format(self.customer.name, self.date_ordered)
    @property
    def shipping(self):
        shipping= False
        orderitems = self.orderitem_set.all()
        for i in orderitems:
            if i.product.digital == False:
                shipping = True
        return shipping

    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total

    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total

class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return str(self.product)

    @property
    def datecreated(self):
        return self.date_added
    
    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total
    

class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    address = models.CharField(max_length=200, null=True)
    city = models.CharField(max_length=200, null=True)
    state = models.CharField(max_length=200, null=True)
    zipcode = models.CharField(max_length=200, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address

class Feedback(models.Model):
    name = models.CharField(max_length=200, null=True)
    email = models.EmailField()
    subject = models.CharField(max_length=200, default='')
    details = models.TextField()
    happy = models.BooleanField(default=False, null=True,blank=True)
    date = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Feedback"

    def __str__(self):
        return  self.email

