from django.shortcuts import render

def index(request):
    return render(request, 'order/index.html')

def payment(request):
    return render(request, 'order/payment.html')