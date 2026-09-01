from django.shortcuts import redirect
from .models import Customer

def customer_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        try:
           
            request.customer = Customer.objects.get(user=request.user)
        except Customer.DoesNotExist:
            return redirect('custlogin')  
        return view_func(request, *args, **kwargs)
    return _wrapped_view
