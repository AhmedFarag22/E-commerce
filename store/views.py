from django.shortcuts import render
from .models import*
from django.http import JsonResponse
import json
import datetime
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .forms import *
from django.shortcuts import render, redirect

from . utils import cookieCart, cartData, guestOrder
# Create your views here.


def registerPage(request):
    form = CreateUserForm()
        
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            
            messages.success(request, 'Account was created for ' + username)
                
            return redirect('login')
    context = {'form':form}
    return render(request, 'store/register.html', context)

def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
            
        user = authenticate(request, username=username, password=password)
            
        if user is not None:
            login(request, user)
            return redirect('/')
            
        else:
            messages.info(request, 'Username OR Password is incorrect')    
            
    
    context = {}
    return render(request, 'store/login.html', context)  

def logoutUser(request):
    logout(request)
    return redirect('login')

def store(request):
    data = cartData(request)
    cartItems = data['cartItems']
    
    #if request.user.is_authenticated:
    #    customer = request.user.customer
    #    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    #    items = order.orderitem_set.all()
    #    cartItems = order.get_cart_items
    #else:
    #    cookieData = cookieCart(request)
    #    cartItems = cookieData['cartItems']
    
    products = Product.objects.all()
    context = {'products':products, 'cartItems':cartItems}
    return render(request, 'store/store.html', context)


def cart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    #if request.user.is_authenticated:
    #    customer = request.user.customer
    #    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    #    items = order.orderitem_set.all()
    #    cartItems = order.get_cart_items
    #else:
    #    cookieData = cookieCart(request)
    #    cartItems = cookieData['cartItems']
    #    order = cookieData['order']
    #    items = cookieData['items']    
        
    context = {'items':items, 'order':order, 'cartItems':cartItems}
    return render(request, 'store/cart.html', context)


def checkout(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    #if request.user.is_authenticated:
    #    customer = request.user.customer
    #    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    #    items = order.orderitem_set.all()
    #    cartItems = order.get_cart_items
    
    #else:
    
    #   # items = []
    #    #order = {'get_cart_total':0, 'get_cart_items':0}
    #   # cartItems = order['get_cart_items']
    
    #    cookieData = cookieCart(request)
    #    cartItems = cookieData['cartItems']
    #    order = cookieData['order']
    #    items = cookieData['items']
    

    
    context = {'items':items, 'order':order, 'cartItems':cartItems}
    return render(request, 'store/checkout.html', context)

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    
    print('Action:', action)
    print('productID:', productId)
    
    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)
    
    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)
        
    orderItem.save()
    
    if orderItem.quantity <= 0:
        orderItem.delete()    
    
    return JsonResponse('Item was added', safe=False)

#from django.views.decorators.csrf import csrf_exempt

#@csrf_exempt
def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp() 
    data = json.loads(request.body)
    
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete = False)
       
        
          
            
    else:
        customer, order = guestOrder(request, data)
    
    total = float(data['form']['total'])
    order.transaction_id = transaction_id
        
    if total == float(order.get_cart_total):
        order.complete = True
    order.save()
    
    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode']
            ) 
    
            
    return JsonResponse('Payment complete', safe=False)


