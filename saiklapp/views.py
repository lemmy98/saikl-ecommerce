from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse
from django.http import JsonResponse
import json
import datetime
from django.forms import inlineformset_factory
from django.contrib.auth.forms import PasswordResetForm, UserCreationForm

from django.contrib.auth import authenticate, login, logout

from django.contrib import messages

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.utils import timezone
from .decorators import unauthenticated_user, allowed_users
from django.views.generic import FormView


from .models import *
from .forms import CreateUserForm, FeedbackForm, ProductForm, OrderForm, CustomerForm,PasswordForgotForm, PasswordResetForm
from .utils import cartData, guestOrder, password_reset_token
from django.core.mail import send_mail
from django.conf import settings

# Create your views here.
def home(request):
   
    context = {}
    return render(request, 'store/home.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def addproduct(request):
    form = ProductForm()
   
    if request.method == 'POST':
        form = ProductForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save()
    
        return redirect(reverse('products'))
       
    context = {'form':form}
    return render(request, 'store/add_product.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def updateproduct(request, pk):
    product = Product.objects.get(id=pk)
    form = ProductForm(instance=product)
   
    if request.method == 'POST':
        form = ProductForm(data=request.POST, files=request.FILES,instance=product)
        if form.is_valid():
            form.save()
            
        return redirect(reverse('products'))
       
    context = {'form':form, 
                'product':product}

    return render(request, 'store/update_product.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['registered customers'])
def productdetail(request, pk):

    products=Product.objects.get(id=pk)
    context={'products':products}

    return render(request,"store/product_details.html",context)



@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def admindash(request):
    orders = Order.objects.all()
    customers = Customer.objects.all()
 
    total_customers = customers.count()

    total_orders = orders.count()
    delivered = orders.filter(complete=True).count()
    pending = orders.filter(complete=False).count()
    
    context = {
        'orders':orders, 
        'customers':customers,
        'total_customers':total_customers,
        'total_orders':total_orders,
        'delivered':delivered,
        'pending':pending,
    }
    return render(request, 'store/admin_dashboard.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['registered customers'])
def usersettings(request):
    customer = request.user.customer
    form = CustomerForm(instance=customer) 

    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES,instance=customer)
        if form.is_valid():
            form.save()


    context = {'form':form}
    return render(request, 'store/usersettings.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def products(request):
    products = Product.objects.all()
    context = {'products':products}
    return render(request, 'store/products.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def customer(request, pk):
    customer = Customer.objects.get  (id=pk)
    orders = customer.order_set.all()
    #orders = request.user.customer.order_set.all()
   
    total_orders = orders.count()

    context = {'customer':customer, 'orders':orders,'total_orders':total_orders}
    return render(request, 'store/customer.html', context)


@unauthenticated_user
def registerPage(request):
    form = CreateUserForm()
   
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')

            group = Group.objects.get(name='registered customers')
            user.groups.add(group)
            Customer.objects.create(
                user = user,
            )

            messages.success(request, 'Account was created for ' + username)
            return redirect('login')

    context = {'form':form}
    return render(request, 'store/register.html', context)


@unauthenticated_user
def loginPage(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')

        else:
            messages.info(request, 'Username OR Password is Incorrect')

    context = {}
    return render(request, 'store/login.html', context)

def logoutUser(request):

    logout(request)
    return redirect('home')


def store(request):
    data = cartData(request)
    cartItems = data['cartItems']
    
    products = Product.objects.all()
    context={'products':products, 'cartItems':cartItems}
    return render(request, 'store/store.html', context)

def cart(request):
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']


    context={'items':items, 'order':order, 'cartItems':cartItems}
    return render(request, 'store/cart.html', context)


def checkout(request):
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context={'items':items, 'order':order, 'cartItems':cartItems}
    return render(request, 'store/checkout.html', context)


@allowed_users(allowed_roles=['registered customers'])
def updateItem(request):
    data = json.loads(request.body)
    ProductId = data['productId']
    action = data['action']

    print('Action:', action)
    print('productId:',ProductId)

    customer = request.user.customer
    product = Product.objects.get(id=ProductId)
    order, created = Order.objects.get_or_create(customer=customer,complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save() 

    if orderItem.quantity <= 0:
        orderItem.delete()



    return JsonResponse('Item was added',safe=False)

# from django.views.decorators.csrf import csrf_exempt

# @csrf_exempt
@login_required(login_url='login')
@allowed_users(allowed_roles=['registered customers'])
def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)


    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer,complete=False)
        

    else:
        customer, order = guestOrder(request, data)
        

    total = float(data['form']['total'])
    order.transaction_id = transaction_id  

    if total == float(order.get_cart_total):
        order.complete = False
    order.save()

    
    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order = order,
            address = data['shipping']['address'],
            city = data['shipping']['city'],
            state = data['shipping']['state'],
            zipcode = data['shipping']['zipcode'],
        ) 


    return JsonResponse('Payment complete!', safe=False)

@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])
def updateOrder(request, pk):
    order = Order.objects.get(id=pk)
    form = OrderForm(instance=order)
    if request.method == 'POST':
            form = OrderForm(request.POST, instance=order)
            if form.is_valid():
                form.save()
                return redirect('admindash')

    context = {'form':form}
    return render(request, 'store/order_form.html', context)



@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])
def deleteOrder(request, pk):
    order = Order.objects.get(id=pk)
    if request.method == "POST":
        order.delete()
        return redirect('admindash')

    context = {'item':order}
    return render(request, 'store/delete.html',  context)



class PasswordForgotView(FormView):
    template_name = "forgotpassword.html"
    form_class = PasswordForgotForm
    success_url = "/forgot-password/?m=s"

    
    def form_valid(self, form):
        #get email form user 
        email = form.cleaned_data.get("email")
        #get current host ip/domain
        url = self.request.META['HTTP_HOST']
        #get customer then user
        customer = Customer.objects.get(user__email=email)
        user = customer.user
        # send mail to user email
        text_content = 'Please Click the link below to reset your password. '
        html_content = url + "/password-reset/" + email + "/" + password_reset_token.make_token(user) + "/"
        send_mail(
            'Password Reset Link | SAIKL',
            text_content + html_content,
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )

        return super().form_valid(form)

    def send_mail(self, valid_data):
        # Send mail logic
        print(valid_data)
        pass

class passwordResetView(FormView):
    template_name = "passwordreset.html"
    form_class = PasswordResetForm
    success_url = "/login/"


    def dispatch(self, request, *args, **kwargs):
        email = self.kwargs.get("email")
        user = User.objects.get(email=email)
        token = self.kwargs.get("token")
        if user is not None and password_reset_token.check_token(user, token):
          pass
        else:
            return redirect(reverse('passwordforgot') + "?m=e")


        return super().dispatch(request, *args, **kwargs)
    

    def form_valid(self, form):
        password = form.cleaned_data['new_password']
        email = self.kwargs.get("email")
        user = User.objects.get(email=email)
        user.set_password(password)
        user.save()
       

        return super().form_valid(form)


@login_required(login_url='login')
@allowed_users(allowed_roles=['registered customers'])
def feedback(request):
    customer = request.user.customer
    form = FeedbackForm(instance=customer)

    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        Feedback.email = customer.email

        if form.is_valid():
            form.save()
            return redirect('thanks')
    else:
        form = FeedbackForm()

    context = {'form': form, 'customer':customer, 'feedback':feedback}
    return render(request, 'store/feedback_form.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['registered customers'])
def thanks(request):
   
    context = {}
    return render(request, 'store/thanks.html', context)

