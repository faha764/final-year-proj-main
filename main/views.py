from django.shortcuts import render, redirect
from .models import CartItem, Product
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import WishlistItem, Product
from decimal import Decimal
from .models import Seller, Customer, Order
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from .models import Category
from .forms import CategoryForm
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from .models import CartItem
from .forms import ProductForm
from .models import Admin
from django.http import JsonResponse
from .models import Customer, ShippingDetail
from .models import OrderItem
from .models import Order
import uuid
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Seller
from django.core.files.base import ContentFile
from django.http import JsonResponse
from .models import Order, OrderItem, Customer, Seller
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.files.base import ContentFile
from django.utils import timezone
from .models import Order, OrderItem 
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
import base64
from django.core.files.base import ContentFile
from django.utils import timezone
from .models import Order, OrderItem, Customer, Seller
from .models import ShippingDetail
from collections import defaultdict
from django.shortcuts import render, get_object_or_404
from .models import Order  
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Order, OrderItem, ShippingDetail
from .models import Order
from .models import Order, ShippingDetail
from .models import ChatRoom, Message
from .models import Product, Customer, Seller

#unique seller email and cnic 
def check_unique(request):
    email = request.GET.get("email")
    cnic = request.GET.get("cnic")
    if email:
        if Seller.objects.filter(email=email).exists():
            return JsonResponse({"valid": False, "message": "Email already exists"})
        return JsonResponse({"valid": True, "message": ""})
    if cnic:
        if Seller.objects.filter(cnic=cnic).exists():
            return JsonResponse({"valid": False, "message": "CNIC already exists"})
        return JsonResponse({"valid": True, "message": ""})
    return JsonResponse({"valid": False, "message": "Invalid request"})


# Customer opens chat with Seller
def chat_room_customer(request, product_id, seller_id):
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('custlogin')
    customer = get_object_or_404(Customer, id=customer_id)
    seller = get_object_or_404(Seller, id=seller_id)
    product = get_object_or_404(Product, id=product_id)
    room, created = ChatRoom.objects.get_or_create(
        customer=customer, seller=seller, product=product
    )


# mark seller messages as read
    room.messages.filter(sender_type="seller", is_read=False).update(is_read=True)

    messages = room.messages.all()

    return render(request, "customer/chat_room.html", {
        "room": room,
        "messages": messages,
        "sender_type": "customer",
        "seller": seller,
        "product": product,
    })


# Seller opens chat
def chat_room_seller(request, product_id, customer_id):
    seller_id = request.session.get('seller_id')
    if not seller_id:
        return redirect('sellerlogin')

    seller = get_object_or_404(Seller, id=seller_id)
    customer = get_object_or_404(Customer, id=customer_id)
    product = get_object_or_404(Product, id=product_id)

    room, created = ChatRoom.objects.get_or_create(
        customer=customer, seller=seller, product=product
    )


# mark customer messages as read
    room.messages.filter(sender_type="customer", is_read=False).update(is_read=True)

    messages = room.messages.all()

    return render(request, "customer/chat_room.html", {
        "room": room,
        "messages": messages,
        "sender_type": "seller",
        "customer": customer,
        "product": product,
    })


#send messages
from django.http import JsonResponse, HttpResponseForbidden
from django.utils.timezone import localtime

def send_message(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)

    if request.method == "POST":
        text = request.POST.get("message")
        sender_type = request.POST.get("sender_type")

        if sender_type not in ["customer", "seller"]:
            return HttpResponseForbidden("Invalid sender.")

        sender_id = room.customer.id if sender_type == "customer" else room.seller.id

        if text and text.strip():
            msg = Message.objects.create(
                room=room,
                sender_type=sender_type,
                sender_id=sender_id,
                text=text
            )

            return JsonResponse({
                "text": msg.text,
                "time": localtime(msg.timestamp).strftime("%I:%M %p"),
                "sender_type": msg.sender_type
            })

    return JsonResponse({"error": "Invalid request"}, status=400)


#msgs recieved
from django.http import JsonResponse
from .models import ChatRoom, Message

def get_messages(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)
    messages = room.messages.order_by("timestamp")
    data = []
    for msg in messages:
        data.append({
            "text": msg.text,
            "time": localtime(msg.timestamp).strftime("%I:%M %p"),
            "sender_type": msg.sender_type,
        })
    return JsonResponse({"messages": data})


# customer chat list
from django.shortcuts import render, get_object_or_404, redirect
from .models import ChatRoom
from .models import Customer, Seller
from .models import ChatRoom, Customer, Seller

def customer_chat_list(request):
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('custlogin')

    customer = Customer.objects.get(id=customer_id)
    chats = ChatRoom.objects.filter(customer=customer).prefetch_related("messages")

    for chat in chats:
        chat.unread_count = chat.messages.filter(sender_type="seller", is_read=False).count()
        chat.last_message = chat.messages.order_by("-timestamp").first()  

    return render(request, "chat/customer_chat_list.html", {"chats": chats})


# Seller chat list

def seller_chat_list(request):
    seller_id = request.session.get('seller_id')
    if not seller_id:
        return redirect('sellerlogin')

    seller = Seller.objects.get(id=seller_id)
    chats = ChatRoom.objects.filter(seller=seller).prefetch_related("messages")

    for chat in chats:
        chat.unread_count = chat.messages.filter(sender_type="customer", is_read=False).count()
        chat.last_message = chat.messages.order_by("-timestamp").first()  

    return render(request, "chat/seller_chat_list.html", {"chats": chats})


#refresh cust chat

from django.http import JsonResponse
from django.utils.timezone import localtime

def refresh_chat_list_customer(request):
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return JsonResponse({'error': 'Not logged in'}, status=403)

    chats = ChatRoom.objects.filter(customer_id=customer_id).prefetch_related("messages")
    data = []
    for chat in chats:
        last_msg = chat.messages.order_by("-timestamp").first()  
        unread_count = chat.messages.filter(sender_type="seller", is_read=False).count()
        data.append({
            "room_id": chat.id,
            "product_id": chat.product.id,
            "seller_id": chat.seller.id,
            "seller_name": chat.seller.name,
            "last_message": last_msg.text if last_msg else "",
            "time": localtime(last_msg.timestamp).strftime("%I:%M %p") if last_msg else "",
            "unread_count": unread_count,
            "seller_image": chat.seller.profile_image.url if chat.seller.profile_image else "/static/images/default_profile.jpeg",
        })

    return JsonResponse({"chats": data})

from django.http import JsonResponse
from django.utils.timezone import localtime
from .models import ChatRoom

#refresh seller chat

def refresh_chat_list_seller(request):
    seller_id = request.session.get('seller_id')
    if not seller_id:
        return JsonResponse({'error': 'Not logged in'}, status=403)

    chats = ChatRoom.objects.filter(seller_id=seller_id).prefetch_related("messages")
    data = []

    for chat in chats:
        if not chat.customer or not chat.product:
            continue  

        last_msg = chat.messages.order_by("-timestamp").first()
        unread_count = chat.messages.filter(sender_type="customer", is_read=False).count()

        data.append({
            "room_id": chat.id,
            "product_id": chat.product.id,
            "customer_id": chat.customer.id,
            "customer_name": chat.customer.name,
            "last_message": last_msg.text if last_msg else "",
            "time": localtime(last_msg.timestamp).strftime("%I:%M %p") if last_msg else "",
            "timestamp": last_msg.timestamp.isoformat() if last_msg else "1970-01-01T00:00:00",
            "unread_count": unread_count,
            "customer_image": getattr(chat.customer, 'profile_image', None) or "/static/images/default_profile.jpeg",

        })

    return JsonResponse({"chats": data})

#notification

def notification(request, role):
    """
    View to display notifications for admin, seller, or customer
    """
    try:
        if role == "seller":
            seller_id = request.session.get("seller_id")  
            if seller_id:
                notifications = Notification.objects.filter(
                    role="seller",
                    target_id=seller_id
                ).order_by('-created_at')
            else:
                notifications = []

        elif role == "customer":
            customer_id = request.session.get("customer_id")  
            if customer_id:
                notifications = Notification.objects.filter(
                    role="customer",
                    target_id=customer_id
                ).order_by('-created_at')
            else:
                notifications = []

        elif role == "admin":
            notifications = Notification.objects.filter(
                role="admin"
            ).order_by('-created_at')

        else:
            notifications = []

    except Exception as e:
        print("Error fetching notifications:", e)
        notifications = []

    context = {
        'notifications': notifications,
        'role': role
    }
    return render(request, 'notification.html', context)


def mark_notification_read(request, id, role):
    """
    View to mark a notification as read
    """
    notification = get_object_or_404(Notification, id=id)
    notification.is_read = True
    notification.save()
    return redirect('notification', role=role)  

from .models import Notification

def create_notification(role, message, target_id=None):
    Notification.objects.create(
        role=role,
        message=message,
        target_id=target_id
    )


#seller order manage

def seller_orders_api(request):
    seller_id = request.session.get('seller_id')
    if not seller_id:
        return JsonResponse({'error': 'Not logged in as seller'}, status=401)

    
    orders = Order.objects.filter(seller_id=seller_id).select_related('customer')

    order_list = []
    for order in orders:
        shipping = ShippingDetail.objects.filter(customer=order.customer).first()
        shipping_data = {
            'full_name': shipping.full_name if shipping else '',
            'address': shipping.address if shipping else '',
            'city': shipping.city if shipping else '',
            'phone': shipping.phone if shipping else '',
            'email': shipping.email if shipping else '',
        }
        order_list.append({
            'id': order.id,
            'status': order.status,
            'shipping': shipping_data,
        })

    return JsonResponse(order_list, safe=False)
def seller_order_detail_api(request, order_id):
    seller_id = request.session.get('seller_id')
    if not seller_id:
        return JsonResponse({'error': 'Not logged in as seller'}, status=401)

    try:
        order = Order.objects.get(id=order_id, seller_id=seller_id)
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)

    items_data = []
    for item in order.items.all():  
        items_data.append({
            'name': item.product_name,
            'quantity': item.quantity,
            'total_price': float(item.price) * item.quantity,
            'image': item.image_url,
        })

    return JsonResponse({
        'id': order.id,
        'items': items_data,
    })


#seller side order status update

@csrf_exempt
def seller_update_order_status(request, order_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)

    try:
        order = Order.objects.get(pk=order_id)
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)

    try:
        print(request.body)

        body = json.loads(request.body)
        new_status = body.get('status', '').lower()
        if new_status not in ['pending', 'confirmed', 'shipping', 'cancelled', 'delivered']:
            return JsonResponse({'error': 'Invalid status'}, status=400)

        order.status = new_status
        order.save()

        if new_status == 'delivered':
            # Notify customer
            create_notification(
                role='customer',
                target_id=order.customer.id,
                message=f"Your Order #{order.id} has been Delivered by the seller."
            )

            # Notify admin
            create_notification(
                role='admin',
                message=f"Order #{order.id} from {order.customer.name} has been Delivered."
            )


        return JsonResponse({'success': True, 'new_status': order.status})
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)


# reupload payment screen shot

@csrf_exempt
def retry_payment(request, order_id):
    if request.method == "POST":
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return JsonResponse({"success": False, "message": "Order not found."}, status=404)

        payment_method = request.POST.get("payment_method")
        screenshot = request.FILES.get("screenshot")

        if not screenshot:
            return JsonResponse({"success": False, "message": "Screenshot is required."})

        if order.payment_screenshot:
            order.payment_screenshot.delete(save=False)

        order.payment_method = payment_method or "unknown"
        order.payment_screenshot = screenshot
        order.status = "Payment Re-uploaded"
        order.save()

        return JsonResponse({"success": True})

    return JsonResponse({"success": False, "message": "Invalid request method."}, status=405)



from collections import defaultdict
from django.http import JsonResponse
from django.utils import timezone
from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from .models import Order, OrderItem, Customer, Seller, Product, CartItem

# order place 

@csrf_exempt
def payment_confirms_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("Incoming Data:", data)

            customer_id = request.session.get('customer_id')
            if not customer_id:
                return JsonResponse({'success': False, 'error': 'User not logged in'}, status=403)

            customer = Customer.objects.get(id=customer_id)

            
            shipping = data.get('shipping')
            method = data.get('paymentMethod')
            screenshot_b64 = data.get('paymentScreenshot')
            cart_items = data.get('cartItems', [])

        
            format, imgstr = screenshot_b64.split(';base64,')
            ext = format.split('/')[-1]
            screenshot_file = ContentFile(
                base64.b64decode(imgstr),
                name=f'screenshot_{timezone.now().strftime("%Y%m%d%H%M%S")}.{ext}'
            )

            
            seller_items = defaultdict(list)
            for item in cart_items:
                seller_name = item.get('seller_name')
                seller_items[seller_name].append(item)

            order_ids = []

            for seller_name, items in seller_items.items():
                seller_obj = Seller.objects.filter(name=seller_name).first()
                if not seller_obj:
                    continue  

                subtotal = sum(item['price'] * item['quantity'] for item in items)
                shipping_fee = 150  
                total = subtotal + shipping_fee

                
                order = Order.objects.create(
                    seller=seller_obj,
                    customer=customer,
                    total_amount=subtotal,
                    shipping_fee=shipping_fee,
                    grand_total=total,
                    payment_method=method,
                    payment_screenshot=screenshot_file,
                )
                order_ids.append(order.id)
                product = Product.objects.filter(name=item['name'], seller=seller_obj).first()
                
                for item in items:
                    
                    if product:
                      CartItem.objects.filter(customer=customer, product=product).delete()
                    
                    if product:
                        if product.quantity < item['quantity']:
                            return JsonResponse({
                                'success': False,
                                'error': f'Not enough stock for {product.name}'
                            }, status=400)

                        
                        product.quantity -= item['quantity']
                        product.save()

                    
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        product_name=item['name'],
                        quantity=item['quantity'],
                        price=item['price'],
                        image_url=item['image'],
                    )

                
                create_notification(
                    role='seller',
                    message=f"You have received a new order (Order ID: {order.id}).",
                    target_id=seller_obj.id
                )
                create_notification(
                    role='admin',
                    message=f"New order placed by {customer.name} for seller {seller_obj.name}.",
                )
                create_notification(
                    role='customer',
                    message=f"Your order (Order ID: {order.id}) has been placed successfully.",
                    target_id=customer.id
                )

           
            return JsonResponse({'success': True, 'order_ids': order_ids})

        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({'success': False, 'error': str(e)}, status=400)


# Payment confirmation page
def paymentconfirmss(request):
    categories = Category.objects.all()
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('custlogin')  

    customer = Customer.objects.get(id=customer_id)
    latest_order = Order.objects.filter(customer=customer).order_by('-created_at').first()

    return render(request, 'customer/paymentconfirmss.html', {
        'order': latest_order,
        'categories':categories
    })


from decimal import Decimal
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import render
from .models import Order
from decimal import ROUND_HALF_UP

#admin order payment

def admin_order_payments(request):
    orders = Order.objects.select_related('customer', 'seller').prefetch_related('items')

    serialized_orders = []

    for order in orders:
       
        commission = (Decimal(order.total_amount) * Decimal('0.10')).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
        seller_gets = ((Decimal(order.total_amount) * Decimal('0.90')) + Decimal(order.shipping_fee)).quantize(Decimal('1'), rounding=ROUND_HALF_UP)

       
        if order.commission_amount != commission or order.seller_earning != seller_gets:
            order.commission_amount = commission
            order.seller_earning = seller_gets
            order.save()

        order.commission = commission
        order.seller_gets = seller_gets

        
        serialized_orders.append({
            'id': order.id,
            'status': order.status,
            'created_at': order.created_at.strftime('%Y-%m-%d %H:%M'),
            'grand_total': int(order.grand_total),
            'commission': int(commission),
            'seller_gets': int(seller_gets),
            'items': [
                {
                    'product_name': item.product_name,
                    'price': int(item.price),
                    'quantity': item.quantity,
                    'image_url': item.image_url
                }
                for item in order.items.all()
            ]
        })

    context = {
        'orders': orders,
        'serialized_orders': json.dumps(serialized_orders, cls=DjangoJSONEncoder),
    }

    return render(request, 'admindashboard/orderpayment.html', context)



#admin order status
from django.shortcuts import render, redirect, get_object_or_404
from decimal import Decimal
from .models import Order

def update_order_status(request, order_id, action):
    order = get_object_or_404(Order, id=order_id)

    if order.status == "Delivered" and action != 'refund':
       return HttpResponseForbidden("This order can no longer be modified.")

    if action == 'approve':
     if order.status != 'Confirmed': 
        order.status = 'Confirmed'
        commission = Decimal(order.total_amount) * Decimal('0.10')
        seller_amount = Decimal(order.total_amount) * Decimal('0.90') + Decimal(order.shipping_fee)

        if hasattr(order, 'commission_amount'):
            order.commission_amount = commission
        if hasattr(order, 'seller_earning'):
            order.seller_earning = seller_amount

        # Notifications for approve
        create_notification(
            role='customer',
            target_id=order.customer.id,
            message = f"Your order #{order.id} has been approved.\nIt will be delivered within 15 days."
        )
        create_notification(
            role='seller',
            target_id=order.seller.id,
            message=f"Order #{order.id} is approved and payment has been received."
        )

    elif action == 'cancel':
        order.status = 'Cancelled by Admin'

        
        order_items = OrderItem.objects.filter(order=order)
        for item in order_items:
            try:
                product = Product.objects.get(name=item.product_name)
                product.quantity += item.quantity
                product.save()
            except Product.DoesNotExist:
                continue

        
        create_notification(
            role='seller',
            target_id=order.seller.id,
            message=f"Order #{order.id} has been cancelled by the admin."
        )
        create_notification(
            role='customer',
            target_id=order.customer.id,
            message=f"Your Order #{order.id} has been cancelled by the admin. You will be refunded soon according to the Craftoria refund policy. For further details, contact us through our Contact Us page."
        )

    elif action == 'notify':
        order.status = 'Payment Re-upload Requested'
        create_notification(
            role='customer',
            target_id=order.customer.id,
            message=f"Admin has requested you to re-upload the payment screenshot for Order #{order.id}."
        )

    elif action == 'refund':
     if order.status != 'Refunded': 
        order.status = 'Refunded'  
        order.refunded = True  

      
        create_notification(
            role='customer',
            target_id=order.customer.id,
            message=f"Your refund for Order #{order.id} has been processed by admin. Please check your email for details."
        )

    order.save()
    return redirect('admindashboard')


from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt  
from django.http import JsonResponse
from .models import Order
from django.utils.timezone import localtime


#cust order cancel

def cancel_order_ajax(request, order_id):
    if request.method == 'POST':
        try:
            order = get_object_or_404(Order, id=order_id, customer_id=request.session.get('customer_id'))

            if not order.is_cancelable():
                return JsonResponse({'success': False, 'message': 'Order not cancelable'})

            # Update status and save cancellation time
            order.status = 'cancelled'
            order.cancelled_at = now()
            order.save(update_fields=['status', 'cancelled_at'])

            # Restore stock
            for item in order.items.all():
                product = item.product
                if product:
                    product.quantity += item.quantity
                    product.save(update_fields=['quantity'])

                    # Notify seller
                    create_notification(
                        role='seller',
                        target_id=product.seller.id,
                        message=f"Order #{order.id} containing '{product.name}' was cancelled by {order.customer.name}."
                    )

            # Notify admin
            create_notification(
                role='admin',
                message=f"Customer {order.customer.name} cancelled Order #{order.id}."
            )

            # Notify customer
            create_notification(
                role='customer',
                target_id=order.customer.id,
                message=(
                    f"Your Order #{order.id} has been successfully cancelled. "
                    "A refund will be processed soon in accordance with Craftify's refund policy. "
                    "For any further assistance, please reach out to us via the Contact Us page."
                )
            )

            # Proper timestamp for frontend
            cancelled_at_str = localtime(order.cancelled_at).strftime('%Y-%m-%d %I:%M %p')

            return JsonResponse({
                'success': True,
                'cancelled_at': cancelled_at_str,
                'order_id': order.id,
                'amount': str(order.grand_total),
            })

        except Order.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Order not found'})
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Invalid request'})

from django.utils.timezone import now, make_aware, localtime, is_naive
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.timezone import make_aware, is_naive, now
from datetime import timedelta

from django.contrib import messages
from .models import Order  
from django.db.models import Q
from django.db.models import Q, Prefetch
from django.utils.timezone import now, is_naive, make_aware
from datetime import timedelta
import pytz
from django.db.models import Count, Q, F

#cust order history

def myorders(request):
    customer_id = request.session.get('customer_id')

    latest_orders = []
    cancelled_orders = []
    to_ship_orders = []
    to_receive_orders = []
    to_review_orders = []
    completed_orders = []

    if customer_id:
        orders = Order.objects.filter(customer_id=customer_id).order_by('-created_at')
        karachi_tz = pytz.timezone('Asia/Karachi')

        for order in orders:
            if is_naive(order.created_at):
                order.created_at = make_aware(order.created_at, timezone=karachi_tz)
            cancel_window = order.created_at + timedelta(hours=24)
            order.is_cancelable = now() < cancel_window

        latest_statuses = ['pending', 'confirmed', 'payment re-uploaded', 'payment re-upload requested']
        for order in orders:
            status_lower = order.status.lower()
            if status_lower in latest_statuses:
                if status_lower == 'confirmed':
                    if order.is_cancelable:
                        latest_orders.append(order)
                else:
                    latest_orders.append(order)

        
        completed_orders = orders.filter(
    items__review__isnull=False
).distinct().prefetch_related(
    Prefetch('items', queryset=OrderItem.objects.filter(review__isnull=False))
)

        cancelled_orders = orders.filter(Q(status__iexact='cancelled') | Q(status__iexact='cancelled by admin')| 
    Q(status__iexact='refunded'))
        to_ship_orders = orders.filter(status__iexact='confirmed')
        to_receive_orders = orders.filter(status__iexact='shipping')

        unreviewed_items_qs = OrderItem.objects.filter(review__isnull=True)
        to_review_orders = orders.filter(
            status__iexact='delivered', 
            items__review__isnull=True
        ).distinct().prefetch_related(
            Prefetch('items', queryset=unreviewed_items_qs)
        )

    return render(request, 'customer/myorders.html', {
        'latest_orders': latest_orders,
        'cancelled_orders': cancelled_orders,
        'to_ship_orders': to_ship_orders,
        'to_receive_orders': to_receive_orders,
        'to_review_orders': to_review_orders,
        'completed_orders': completed_orders,
    })


# product review
from django.views.decorators.http import require_POST

@require_POST
@require_POST
def submit_product_review(request, item_id):
    customer_id = request.session.get('customer_id')
    order_item = get_object_or_404(OrderItem, id=item_id, order__customer_id=customer_id)

    review_text = request.POST.get('review_text')
    rating = request.POST.get('rating', 5)
    image = request.FILES.get('image')

    if review_text:
        ProductReview.objects.create(
            order_item=order_item,
            customer_id=customer_id,
            review_text=review_text,
            rating=rating,
            image=image
        )

        messages.success(request, "")
    else:
        messages.error(request, "Review text cannot be empty.")

    return redirect('customerdashboard')

from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.http import HttpResponseForbidden
from .models import ProductReview, Seller
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import ProductReview
from django.shortcuts import render
from .models import ProductReview
from .models import ProductReview, Product


#seller review reply

def reviews_rating_view(request):
    seller_id = request.session.get('seller_id')

    if not seller_id:
        return render(request, 'seldashboard/reviewsrating.html', {
            'reviews': [],
            'error': 'You must be logged in as a seller.'
        })

    seller_products = Product.objects.filter(seller_id=seller_id).values_list('name', flat=True)
    reviews = ProductReview.objects.select_related('customer', 'order_item')\
                                   .filter(order_item__product_name__in=seller_products)

    return render(request, 'seldashboard/reviewsrating.html', {'reviews': reviews})

   

import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils.timezone import now
from .models import ProductReview

@csrf_exempt
def send_reply_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        review_id = data.get('review_id')
        reply_text = data.get('reply_text')

        try:
            review = ProductReview.objects.get(id=review_id)
            review.seller_reply = reply_text
            review.reply_date = now()
            review.save()
            return JsonResponse({'success': True})
        except ProductReview.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Review not found'}, status=404)

    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)


# views.py
from django.http import JsonResponse
from .models import OrderItem, ProductReview



def cancel_order(request, order_id):
    if request.method == "POST":
        customer_id = request.session.get('customer_id')
        order = get_object_or_404(Order, id=order_id, customer_id=customer_id)

        if order.status.lower() == 'pending':  
            order.status = 'Cancelled'
            order.save()

            

            messages.success(request, "Order cancelled successfully.")
        else:
            messages.error(request, "This order cannot be cancelled.")

    return redirect('myorders')

from .models import Category
from .forms import CategoryForm

from django.http import JsonResponse
from .models import Order, OrderItem  

def order_details_ajax(request, order_id):
    if request.method == 'GET':
        try:
            order = Order.objects.get(id=order_id)
            order_items = order.items.all()  

            items_data = []
            total_amount = 0

            for item in order_items:
                subtotal = item.price * item.quantity
                total_amount += subtotal
                items_data.append({
                    'product_name': item.product_name,
                    'quantity': item.quantity,
                    'price': float(item.price),
                    'image_url': item.image_url,
                    'subtotal': float(subtotal),
                })

            return JsonResponse({
                'success': True,
                'items': items_data,
                'grand_total': float(order.grand_total) 
            })

        except Order.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Order not found.'})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method.'})


#shipping detail

@require_POST
def save_shipping_detail(request):
    try:
        data = json.loads(request.body)
        customer_id = data.get('customer_id')

        if not customer_id:
            return JsonResponse({"error": "Customer ID is required"}, status=400)

        customer = Customer.objects.get(id=customer_id)

        # Check if a shipping detail already exists for this customer
        shipping_detail, created = ShippingDetail.objects.get_or_create(customer=customer)

        # Update the fields regardless of create/update
        shipping_detail.full_name = data.get('full_name', shipping_detail.full_name)
        shipping_detail.email = data.get('email', shipping_detail.email)
        shipping_detail.address = data.get('address', shipping_detail.address)
        shipping_detail.city = data.get('city', shipping_detail.city)
        shipping_detail.phone = data.get('phone', shipping_detail.phone)
        shipping_detail.save()

        return JsonResponse({"message": "ok"})

    except Customer.DoesNotExist:
        return JsonResponse({"error": "Customer not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


from .models import WishlistItem, Customer
from django.http import JsonResponse
from .models import WishlistItem, Product, Customer
from django.shortcuts import render, get_object_or_404, redirect

#wishlist


def wishlistok(request):
    categories = Category.objects.all()
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('custlogin')

    customer = get_object_or_404(Customer, id=customer_id)
    items = WishlistItem.objects.filter(customer=customer).select_related('product')
    
    return render(request, 'customer/wishlistok.html', {'items': items, 'categories': categories})

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

@csrf_exempt
def add_to_wishlist(request):
    if request.method == "POST":
        if not request.session.get("customer_id"):
            return JsonResponse({'status': 'not_logged_in'})
        
        product_id = request.POST.get("product_id")
        if not product_id:
            return JsonResponse({'status': 'error', 'message': 'No product ID'})

        try:
            customer = Customer.objects.get(id=request.session["customer_id"])
            product = Product.objects.get(id=product_id)

            # Check if already exists
            if WishlistItem.objects.filter(customer=customer, product=product).exists():
                return JsonResponse({'status': 'exists'})

            WishlistItem.objects.create(customer=customer, product=product)
            return JsonResponse({'status': 'added'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

def remove_from_wishlist(request, item_id):

    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('custlogin')  # redirect to login if not logged in

    item = get_object_or_404(WishlistItem, id=item_id, customer_id=customer_id)
    item.delete()
    return redirect('wishlistok')  

def remove_from_wishlist_ajax(request, item_id):
    if request.method == 'POST':
        try:
            item = WishlistItem.objects.get(id=item_id)
            item.delete()
            return JsonResponse({'status': 'success'})
        except WishlistItem.DoesNotExist:
            return JsonResponse({'status': 'not_found'}, status=404)
    return JsonResponse({'status': 'invalid'}, status=400)

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.mail import send_mail
from .models import ContactMessage
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import ContactMessage
from .models import Category   

#contact us

def contactus(request):
    categories = Category.objects.all()
    
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        if name and email and subject and message:
            
            ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message
            )

            
            full_message = f"From: {name} <{email}>\n\n{message}"
            send_mail(
                subject=f"Contact Form: {subject}",
                message=full_message,
                from_email='craftify535@gmail.com',
                recipient_list=['craftify966@gmail.com'],
                fail_silently=True
            )

            messages.success(request, "Your message has been sent successfully.")
            return redirect('contactus')
        else:
            messages.error(request, "All fields are required!")

    return render(request, 'customer/contactus.html', {'categories': categories})


#cart 


from .models import CartItem, Product, Customer, Category
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

def cart_vie(request):
    categories = Category.objects.all()
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('custlogin')

    customer = get_object_or_404(Customer, id=customer_id)
    items = CartItem.objects.filter(customer=customer).select_related('product')
    
    return render(request, 'customer/cart_vie.html', {
        'items': items,
        'categories': categories
    })

@csrf_exempt
def add_to_cart(request):
    if request.method == "POST":
        if not request.session.get("customer_id"):
            return JsonResponse({'status': 'not_logged_in'})

        product_id = request.POST.get("product_id")
        quantity = int(request.POST.get("quantity", 1))

        if not product_id:
            return JsonResponse({'status': 'error', 'message': 'No product ID'})

        try:
            customer = Customer.objects.get(id=request.session["customer_id"])
            product = Product.objects.get(id=product_id)

            cart_item, created = CartItem.objects.get_or_create(customer=customer, product=product)
            if not created:
                cart_item.quantity += quantity
            else:
                cart_item.quantity = quantity
            cart_item.save()
            return JsonResponse({'status': 'added' if created else 'updated'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

def remove_from_cart(request, item_id):
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('custlogin')

    item = get_object_or_404(CartItem, id=item_id, customer_id=customer_id)
    item.delete()
    return redirect('cart_vie')

@csrf_exempt
def remove_from_cart_ajax(request, item_id):
    if request.method == 'POST':
        try:
            item = CartItem.objects.get(id=item_id)
            item.delete()
            return JsonResponse({'status': 'success'})
        except CartItem.DoesNotExist:
            return JsonResponse({'status': 'not_found'}, status=404)
    return JsonResponse({'status': 'invalid'}, status=400)

@csrf_exempt
def update_cart_quantity(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            item_id = data.get("item_id")
            quantity = int(data.get("quantity"))

            if quantity < 1:
                return JsonResponse({"status": "error", "message": "Quantity must be at least 1"}, status=400)

            item = CartItem.objects.get(id=item_id)
            item.quantity = quantity
            item.save()
            return JsonResponse({"status": "success", "new_total": item.total_price()})
        except CartItem.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Item not found"}, status=404)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return JsonResponse({"status": "invalid_method"}, status=405)

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import CartItem 

@csrf_exempt
def delete_all_cart_items(request):
    if request.method == 'POST':
        customer_id = request.session.get('customer_id')
        if not customer_id:
            return JsonResponse({'status': 'error', 'message': 'User not logged in'})

        CartItem.objects.filter(customer_id=customer_id).delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def seller_profile_by_admin(request, seller_id):
    seller = get_object_or_404(Seller, id=seller_id)
    return render(request, 'seldashboard/sellerprofilee.html', {'seller': seller})

def welcome(request):
    return render(request, "customer/welcome.html")


#admin dashboard

from django.db.models import Q
from .models import Notification

def admindashboard(request):
    if not request.session.get("admin_id"):
        return redirect("Adminlogin")  
    
    
    unread_notifications_count = Notification.objects.filter(
        role="admin",
        is_read=False,
        target_id__isnull=True
    ).count()

    return render(request, "admindashboard/admindashboard.html", {
        "unread_notifications_count": unread_notifications_count
    })


#user management

def usermanagement(request):
    sellers = Seller.objects.all()
    customers = Customer.objects.all()
    return render(request, 'admindashboard/usermanagement.html', {
        'sellers': sellers,
        'customers': customers
    })
from django.shortcuts import get_object_or_404

def toggle_seller_status(request, seller_id):
    seller = get_object_or_404(Seller, id=seller_id)
    if seller.status == 'Active':
        seller.status = 'Suspended'
    else:
        seller.status = 'Active'
    seller.save()
    return redirect('admindashboard')  

def toggle_customer_status(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    if customer.status == 'Active':
        customer.status = 'Suspended'
    else:
        customer.status = 'Active'
    customer.save()
    return redirect('admindashboard')



def category(request):
    return render(request, 'admindashboard/admincategory.html') 
def adminlogin(request):
    return render(request, 'admindashboard/adminlogin.html')
def manageorder(request):
    return render(request, 'seldashboard/manageorder.html')
def sellerprofilee(request):
    return render(request, 'seldashboard/sellerprofilee.html')


 
from .models import Product

from django.shortcuts import render
from .models import Product, Category

#home

def homeee(request):
    trending_products = Product.objects.filter(is_trending=True)[:5]
    featured_products = Product.objects.filter(is_featured=True)[:5]
    categories = Category.objects.all()

    return render(request, 'customer/homeee.html', {
        'trending': trending_products,
        'featured': featured_products,
        'categories': categories
    })

#search products

def search_products(request):
    
    query = request.GET.get('q')  
    results = []

    if query:
        results = Product.objects.filter(name__icontains=query)  
    categories = Category.objects.all()
    return render(request, 'customer/search_results.html', {
        'query': query,
        'results': results,
        'categories': categories
    })


 
#chatbox

def chatbox(request, product_id):
    categories = Category.objects.all()
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'customer/chatbox.html', {'product': product,'categories': categories})
def checkout(request):
    categories = Category.objects.all()
    return render(request, 'customer/checkout.html',{'categories': categories}) 

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Customer
from django.views.decorators.cache import never_cache
from django.contrib import messages

#cust signup

def custsignup_view(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        name = request.POST.get('name').strip()
        email = request.POST.get('email').strip().lower()
        contact = request.POST.get('contact').strip()
        password = request.POST.get('password')

        
        if Customer.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered as a Customer.')
            return redirect('custsignup')

      
        hashed_password = make_password(password)

       
        customer = Customer(
            name=name,
            email=email,
            contact=contact,
            password=hashed_password
        )
        customer.save()

        request.session['customer_id'] = customer.id
        request.session['customer_name'] = customer.name  

        messages.success(request, "")

      
        return redirect('homeee')

    return render(request, 'customer/custsignup.html', {'categories': categories})

from django.contrib import messages
from django.shortcuts import render, redirect
from .models import Customer
from django.contrib.auth.hashers import check_password


#cust login

def custlogin(request):
    categories = Category.objects.all()

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            customer = Customer.objects.get(email=email)

            if customer.status == 'Suspended':
                messages.error(request, 'Your account is suspended. Please contact admin.')
                return redirect('custlogin')

           
            if check_password(password, customer.password):
                customer.status = 'Active'  
                customer.save(update_fields=['status'])
                request.session['customer_id'] = customer.id
                return redirect('homeee')  
            else:
                messages.error(request, 'Incorrect password. Please try again.')
                return redirect('custlogin')

        except Customer.DoesNotExist:
            messages.error(request, 'No account found with this email. Please sign up.')
            return redirect('custlogin')

    return render(request, 'customer/custlogin.html', {'categories': categories})

def customer_logout(request):
    customer_id = request.session.get('customer_id')
    if customer_id:
       
        Customer.objects.filter(id=customer_id).update(status='Inactive')

       
        del request.session['customer_id']

    return redirect('homeee')  

#prod detail page

from django.shortcuts import render, get_object_or_404
from .models import Product, ProductReview, Category

def productdetail(request, product_id):
    categories = Category.objects.all()
    product = get_object_or_404(Product, id=product_id)
    reviews = ProductReview.objects.filter(order_item__product_name=product.name).select_related('order_item')

    return render(request, 'customer/productdetail.html', {
        'product': product,
        'categories': categories,
        'reviews': reviews,
    })


 
from .models import Product, Category  

#trending and featured prod

def trendingproducts(request):
    trending_products = Product.objects.filter(is_trending=True)
    categories = Category.objects.all()  
    return render(request, 'customer/trendingproducts.html', {
        'trending_products': trending_products,
        'categories': categories,
    })

def featuredproducts(request):
    featured_products = Product.objects.filter(is_featured=True)
    categories = Category.objects.all()  
    return render(request, 'customer/featuredproducts.html', {
        'featured_products': featured_products,
        'categories': categories,
    }) 

from django.shortcuts import render, get_object_or_404
from .models import Customer, ShippingDetail
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Category, Customer, ShippingDetail, ChatRoom, Notification

#cust dashboard

def customerdashboard(request):
    categories = Category.objects.all()
    customer_id = request.session.get('customer_id')

    if not customer_id:
        messages.error(request, "Please login first.")
        return redirect('custlogin')

    customer = get_object_or_404(Customer, id=customer_id)

    if customer.status == 'Suspended':
        del request.session['customer_id']
        messages.error(request, "Your account is suspended. Please contact admin.")
        return redirect('custlogin')

    try:
        shipping_detail = ShippingDetail.objects.get(customer=customer)
    except ShippingDetail.DoesNotExist:
        shipping_detail = None

    rooms = ChatRoom.objects.filter(customer=customer).select_related("product", "seller")

   
    unread_notifications_count = Notification.objects.filter(
        role='customer',
        target_id=customer_id,
        is_read=False
    ).count()

  
    unread_chat_count = 0
    for room in rooms:
        unread_chat_count += room.messages.filter(sender_type="seller", is_read=False).count()

    return render(request, 'customer/customerdashboard.html', {
        'customer': customer,
        'shipping_detail': shipping_detail,
        'categories': categories,
        'rooms': rooms,
        'unread_notifications_count': unread_notifications_count,
        'unread_chat_count': unread_chat_count,
    })


def checkout(request):
    
    categories = Category.objects.all()
    return render(request, 'customer/checkout.html',{'categories': categories}) 

from django.shortcuts import render, redirect
from .models import Seller

def update_seller_status(request, seller_id, action):
    seller = Seller.objects.get(id=seller_id)
    if action == 'approve':
        seller.status = 'Active'
    elif action == 'suspend':
        seller.status = 'Suspended'
    seller.save()
    return redirect('usermanagement')

def update_customer_status(request, customer_id, action):
    customer = Customer.objects.get(id=customer_id)
    if action == 'approve':
        customer.status = 'Active'
    elif action == 'suspend':
        customer.status = 'Suspended'
    customer.save()
    return redirect('usermanagement')
def orderpayment(request):
    orders = Order.objects.select_related('seller', 'customer')
    return render(request, 'admindashboard/orderpayment.html', {'orders': orders})



from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from .models import Order

#seller payout

def sellerpayout(request):
   
    payouts = Order.objects.filter(
        Q(status__iexact="delivered") | Q(status__iexact="completed")
     )

    context = {
        "orders": payouts  
    }
    return render(request, "admindashboard/sellerpayout.html", context)


@csrf_exempt
def send_payout(request, order_id):
   
    order = get_object_or_404(
        Order,
        Q(id=order_id) & (
            Q(status__iexact="delivered") | Q(status__iexact="completed")
        )
    )


    if request.method == 'POST':
        txn_id = request.POST.get('transaction_id', '').strip()

        if not txn_id:
            messages.error(request, "Transaction ID is required.")
            return redirect('admindashboard')

       
        order.transaction_id = txn_id
        order.payout_status = 'Sent'  
        order.save()
       
        create_notification(
                role='seller',
                target_id=order.seller.id,
             message=f"Payout for Order #{order.id} has been sent. Transaction ID: {txn_id}, Amount: {order.seller_gets()}"
            )
        

    return redirect('admindashboard')


#admin category

from django.http import JsonResponse

def admincategory(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "")
            return redirect('admindashboard')  
        else:
            messages.error(request, "")
    else:
        form = CategoryForm()
    
    categories = Category.objects.all()
    return render(request, 'admindashboard/admincategory.html', {'form': form, 'categories': categories})

def category_detail(request, category_id):
    category = get_object_or_404(Category, id=id)
    return render(request, 'category_detail.html', {'category': category})

    
def edit_category(request, cat_id):
    category = get_object_or_404(Category, id=cat_id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('admindashboard')
    else:
        form = CategoryForm(instance=category)

    return render(request, 'admindashboard/edit_category.html', {'form': form, 'category': category})
    

def delete_category(request, cat_id):
    category = get_object_or_404(Category, id=cat_id)
    if request.method == 'POST':
        category.delete()
    return redirect('admindashboard') 
from .models import Product, Category

def category_products(request, cat_id):
    categories = Category.objects.all()
    category = get_object_or_404(Category, id=cat_id)
    products = Product.objects.filter(category=category)
    return render(request, 'customer/category_products.html', {
        'category': category,
        'products': products,
        'categories':categories,
    })
from django.shortcuts import render, get_object_or_404
from .models import Category, Product

def admin_category_products(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(category=category)

    return render(request, "admindashboard/admin_category_products.html", {
        "category": category,
        "products": products,
    })

#cust terms and conditions'

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import CartItem, Product
import json



def termcondition(request):
    return render(request, 'customer/termcondition.html')
def custterms(request):
    categories = Category.objects.all()
    return render(request, 'customer/custterms.html' ,{'categories':categories,})
def refund(request):
    categories = Category.objects.all()
    return render(request, 'customer/refund.html',{'categories':categories,})
def exchange(request):
    categories = Category.objects.all()
    return render(request, 'customer/exchange.html',{'categories':categories,})
def privacypolicy(request):
    categories = Category.objects.all()
    return render(request, 'customer/privacypolicy.html',{'categories':categories,})
def aboutuss(request):
    categories = Category.objects.all()
    return render(request, 'customer/aboutuss.html',{'categories':categories,})
def helpcenter(request):
    categories = Category.objects.all()
    return render(request, 'customer/helpcenter.html',{'categories':categories,})
def paymentconfirms(request):
    categories = Category.objects.all()
    return render(request, 'customer/paymentconfirms.html',{'categories':categories,})
def forgetpassword(request):
    return render(request, 'customer/forgetpassword.html')
def selectpayment(request):
    categories = Category.objects.all()
    return render(request, 'customer/selectpayment.html',{'categories':categories,})

from django.shortcuts import redirect
from .models import ChatRoom
from django.db.models import Sum, F
from decimal import Decimal
from .models import OrderItem, Order
from django.db.models import ExpressionWrapper, FloatField



from django.db.models import ExpressionWrapper, FloatField, F, Sum, Avg
from decimal import Decimal
from .models import OrderItem, Product, ProductReview


from django.db.models import ExpressionWrapper, FloatField, F, Sum, Avg
from decimal import Decimal
from django.shortcuts import render
from django.db.models import Sum, Avg


    # rest of the code

from datetime import date, timedelta
from django.db.models import Sum, F, FloatField, ExpressionWrapper, Avg

from datetime import date, timedelta
from django.db.models import Sum, F, FloatField, ExpressionWrapper, Avg
from django.shortcuts import render, redirect

from datetime import datetime, timedelta, date
from django.utils import timezone
from django.db.models import Sum, F, FloatField, ExpressionWrapper, Avg
from django.shortcuts import render, redirect
from .models import OrderItem  # اپنے ماڈل کے مطابق import کریں

def seller_earnings(request):
    seller_id = request.session.get('seller_id')
    if not seller_id:
        return redirect('sellerlogin')

    print("Seller ID:", seller_id)
    print("All OrderItems for seller:", OrderItem.objects.filter(product__seller_id=seller_id))

    # Filter logic
    filter_type = request.GET.get('filter')
    date_filter = {}

    now = timezone.now()

    if filter_type == 'today':
        # آج کی date کے start اور end
        today_start = datetime.combine(now.date(), datetime.min.time())
        today_end = datetime.combine(now.date(), datetime.max.time())
        today_start = timezone.make_aware(today_start)
        today_end = timezone.make_aware(today_end)
        date_filter = {'order__created_at__range': (today_start, today_end)}

    elif filter_type == 'week':
        week_start = now - timedelta(days=7)
        date_filter = {'order__created_at__gte': week_start}

    elif filter_type == 'month':
        month_start = now - timedelta(days=30)
        date_filter = {'order__created_at__gte': month_start}

    # ----------------- NEW LINES START -----------------
    product_earnings = (
        OrderItem.objects
        .filter(
            product__seller_id=seller_id,
            order__status='Delivered',   # make sure status matches exactly
            **date_filter
        )
        .values('product_name', 'image_url')   # use OrderItem fields
        .annotate(
            total_quantity=Sum('quantity'),
            total_earned=Sum(F('price') * F('quantity'))
        )
    )
    # ----------------- NEW LINES END ----------------- 

    grand_total = sum(item['total_earned'] or 0 for item in product_earnings)

    return render(request, 'seldashboard/earnings.html', {
        'product_earnings': product_earnings,
        'grand_total': grand_total
    })




#seller dashboard

def seldashboardok(request):
    seller_id = request.session.get('seller_id')
    if not seller_id:
        return redirect('sellerlogin')

    from .models import Seller, Notification, ChatRoom
    try:
        seller = Seller.objects.get(id=seller_id)
        if seller.status == 'Suspended':
            del request.session['seller_id']
            return redirect('sellerlogin')
    except Seller.DoesNotExist:
        return redirect('sellerlogin')

    # chats & notifications (unchanged)
    rooms = ChatRoom.objects.filter(seller=seller).select_related("product", "customer").prefetch_related("messages")
    unread_notifications_count = Notification.objects.filter(role='seller', target_id=seller.id, is_read=False).count()

    unread_chat_count = sum(
        room.messages.filter(sender_type="customer", is_read=False).count()
        for room in rooms
    )

    total_unread_count = unread_notifications_count + unread_chat_count

    # ==========================
    # 💰 EARNINGS LOGIC
    # ==========================
    


    return render(request, 'seldashboard/seldashboardok.html', {
        'seller': seller,
        'rooms': rooms,
        'unread_notifications_count': unread_notifications_count,
        'unread_chat_count': unread_chat_count,
        'total_unread_count': total_unread_count,
       
    })


#seller manage prod

from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Seller
def manproductok(request):
    seller_id = request.session.get('seller_id')
    if not seller_id:
        return redirect('sellerlogin')
    
    seller = get_object_or_404(Seller, id=seller_id)
    query = request.GET.get('q')

    if query:
        products = Product.objects.filter(seller=seller, name__icontains=query).order_by('-created_at')
    else:
        products = Product.objects.filter(seller=seller).order_by('-created_at')

    return render(request, 'seldashboard/manproductok.html', {'products': products})


from django.shortcuts import render, redirect
from .models import Seller, Product
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Seller, Category
from django.template.loader import render_to_string
from django.http import JsonResponse

#seller add prod

def addproduct(request):
    seller_id = request.session.get('seller_id')
    if not seller_id:
        return redirect('sellerlogin')

    try:
        seller = Seller.objects.get(id=seller_id)
    except Seller.DoesNotExist:
        return redirect('sellerlogin')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)

        if form.is_valid():
            product = form.save(commit=False)
            product.seller = seller
            product.created_at = timezone.now()
            product.save()

           
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                html = render_to_string('seldashboard/addproduct_success.html', {'message': 'Product added successfully!'})
                return JsonResponse({'html': html})

            return redirect('seldashboardok')

        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                html = render_to_string('seldashboard/addproduct_form.html', {'form': form})
                return JsonResponse({'html': html})

            return render(request, 'seldashboard/addproduct.html', {'form': form})
    else:
        form = ProductForm()

    return render(request, 'seldashboard/addproduct.html', {'form': form})

# edit prod

from django.shortcuts import render, redirect, get_object_or_404
from .models import Product
from .forms import ProductForm

def editproduct(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save(commit=False)
            
            # Convert customized string to boolean
            customized_value = request.POST.get('customized')
            if customized_value == 'Yes':
                product.customized = True
            elif customized_value == 'No':
                product.customized = False

            product.save()
            
           
            return redirect('seldashboardok')  

    else:
        form = ProductForm(instance=product)

    return render(request, 'seldashboard/editproduct.html', {'form': form, 'product': product})

#delete prod
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product

def delete_product(request, product_id):
    if request.method == "POST":
        product = get_object_or_404(Product, id=product_id)
        product.delete()
    return redirect('seldashboardok')  

#seller terms and conditions

def selfaqs(request):
    return render(request, 'seldashboard/selfaqs.html') 
def termsandconditions(request):
    return render(request, 'seldashboard/termsandconditions.html') 

from django.shortcuts import render, redirect
from .models import Seller
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from .models import Seller, Customer
from django.db import IntegrityError
from django.contrib.auth.hashers import make_password

#seller signup

def sellersignup_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        contact = request.POST.get('contact')
        shop_name = request.POST.get('shop_name')
        cnic = request.POST.get('cnic')
        account_type = request.POST.get('account_type')
        account_number = request.POST.get('account_number')
        account_holder_name = request.POST.get('account_holder_name')
        password = request.POST.get('password')

        context = {
            'name': name,
            'email': email,
            'contact': contact,
            'shop_name': shop_name,
            'cnic': cnic,
            'account_type': account_type,
            'account_number': account_number,
            'account_holder_name': account_holder_name,
        }

       
        if Customer.objects.filter(email=email, status='Active').exists():
            context['error'] = 'This email is already registered as an active Customer. Please use a different email or login as Customer.'
            return render(request, 'seldashboard/sellersignup.html', context)

        if Seller.objects.filter(email=email, status='Active').exists():
            context['error'] = 'Email is already registered as an active Seller.'
            return render(request, 'seldashboard/sellersignup.html', context)

        if Seller.objects.filter(cnic=cnic).exists():
            context['error'] = 'This CNIC is already registered with another seller.'
            return render(request, 'seldashboard/sellersignup.html', context)

        if Seller.objects.filter(email=email, status='Suspended').exists() or \
           Customer.objects.filter(email=email, status='Suspended').exists():
            context['error'] = 'This email is linked to a suspended account. Please contact admin.'
            return render(request, 'seldashboard/sellersignup.html', context)

        try:
            seller = Seller(
                name=name,
                email=email,
                contact=contact,
                shop_name=shop_name,
                cnic=cnic,
                account_type=account_type,
                account_number=account_number,
                account_holder_name=account_holder_name,
                password=make_password(password)
            )
            seller.save()
        except IntegrityError:
            context['error'] = 'This email or CNIC is already registered.'
            return render(request, 'seldashboard/sellersignup.html', context)

        create_notification(
            role='admin',
            message=f"New seller {seller.name} has signed up."
        )

        request.session['seller_id'] = seller.id
        return redirect('createprofile')

    return render(request, 'seldashboard/sellersignup.html')

#seller login

from django.contrib.auth.hashers import check_password
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import Seller

def sellerlogin(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            seller = Seller.objects.get(email=email)

            
            if seller.status == 'Suspended':
                messages.error(request, 'Your account is suspended. Please contact admin.', extra_tags='login')
                return redirect('sellerlogin')

            
            if check_password(password, seller.password):
               
                seller.status = 'Active'
                seller.save(update_fields=['status'])
                request.session['seller_id'] = seller.id
                request.session['role'] = 'seller'
                request.session.modified = True
                if not seller.full_name or not seller.username or not seller.city:
                    return redirect('createprofile')
                else:
                    return redirect('seldashboardok')

            else:
                messages.error(request, 'Incorrect password.', extra_tags='login')
                return redirect('sellerlogin')
        except Seller.DoesNotExist:
            messages.error(request, 'No account found with this email.', extra_tags='login')
            return redirect('sellerlogin')

    return render(request, 'seldashboard/sellerlogin.html')

def sellerlogout(request):
    seller_id = request.session.get('seller_id')
    if seller_id:
       
        Seller.objects.filter(id=seller_id).update(status='Inactive')
        del request.session['seller_id']

    
    return redirect(request.META.get('HTTP_REFERER', 'homeee'))


#seller redirect

from django.shortcuts import redirect, get_object_or_404

def seller_redirect(request):
    seller_id = request.session.get('seller_id')
    if not seller_id:
        return redirect('sellersignup')

   
    try:
        seller = Seller.objects.get(id=seller_id)
    except Seller.DoesNotExist:
        return redirect('sellersignup')

    if not seller.full_name or not seller.username or not seller.city:
        return redirect('createprofile')
    else:
        return redirect('seldashboardok')


#seller profile

def createprofile(request):
    if request.method == 'POST':
        seller_id = request.session.get('seller_id')
        if not seller_id:
            return redirect('sellersignup')

        try:
            seller = Seller.objects.get(id=seller_id)
        except Seller.DoesNotExist:
            messages.error(request, "Seller not found.")
            return redirect('sellersignup')

      
        seller.full_name = request.POST.get('full_name', '')
        seller.username = request.POST.get('username', '')
        seller.dob = request.POST.get('dob', '')

        experience = request.POST.get('experience')
        seller.experience = int(experience) if experience else None

        seller.skills = request.POST.get('skills', '')
        seller.city = request.POST.get('city', '')
        seller.additional_details = request.POST.get('additional_details', '')

       
        if 'profile_image' in request.FILES:
            seller.profile_image = request.FILES['profile_image']

        seller.save()

        return redirect('seldashboardok')
    return render(request, 'seldashboard/createprofile.html')

from django.shortcuts import render, get_object_or_404
from .models import Seller


def sellerprofilee(request, seller_id=None):
    
    role = None
    if request.session.get("customer_id"):
        role = "customer"
    elif request.session.get("seller_id"):
        role = "seller"
    elif request.session.get("admin_id"):
        role = "admin"

    if seller_id is None:
        seller_id = request.session.get("seller_id")
        if not seller_id:
            return redirect("sellersignup")

    seller = Seller.objects.get(id=seller_id)
    products = Product.objects.filter(seller=seller).order_by("-created_at")

  
    is_owner = (role == "seller" and request.session.get("seller_id") == seller_id)
    is_owner = True 
    return render(request, "seldashboard/sellerprofilee.html", {
        "seller": seller,
        "products": products,
        "role": role,
        "is_owner": is_owner,
    })


def view_seller_profile(request, seller_id):
    seller = get_object_or_404(Seller, id=seller_id)
    products = Product.objects.filter(seller=seller)
    return render(request, 'seldashboard/selprof.html', {
        'seller': seller,
        'products': products
    })
def view_seller_prof(request, seller_id):
    seller = get_object_or_404(Seller, id=seller_id)
    products = Product.objects.filter(seller=seller)
    return render(request, 'seldashboard/selprofile.html', {
        'seller': seller,
        'products': products
    })
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Seller  

def editprofile(request):
    seller_id = request.session.get('seller_id')
    if not seller_id:
        return redirect('sellersignup')

    seller = Seller.objects.get(id=seller_id)

    if request.method == 'POST':
        seller.full_name = request.POST.get('full_name')
        seller.username = request.POST.get('username')
        seller.dob = request.POST.get('dob')
        seller.experience = request.POST.get('experience')
        seller.skills = request.POST.get('skills')
        seller.city = request.POST.get('city')
        seller.additional_details = request.POST.get('additional_details')

        if request.FILES.get('profile_image'):
            seller.profile_image = request.FILES['profile_image']

        seller.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('seldashboardok')

    return render(request, 'seldashboard/editprofile.html', {'seller': seller})

#admin login

def Adminlogin(request):
    if request.method == "POST":
        email = request.POST.get('email').strip()   
        password = request.POST.get('password').strip()

        try:
            admin_user = Admin.objects.get(email=email)
        except Admin.DoesNotExist:
            messages.error(request, "Email not registered.")
            return render(request, 'admindashboard/Adminlogin.html')

        if check_password(password, admin_user.password):
            request.session['admin_id'] = admin_user.id

            
            admin_user.status = "Active"
            admin_user.save(update_fields=["status"])

            return redirect('admindashboard')
        else:
            messages.error(request, "Incorrect password.")
            return render(request, 'admindashboard/Adminlogin.html')

    return render(request, 'admindashboard/Adminlogin.html')
def Adminlogout(request):
    admin_id = request.session.get('admin_id')
    if admin_id:
        try:
            admin_user = Admin.objects.get(id=admin_id)
            admin_user.status = "Inactive"   
            admin_user.save(update_fields=["status"])
        except Admin.DoesNotExist:
            pass
        request.session.flush()  

    messages.success(request, "")
    return redirect('Adminlogin')

 
# Admin forgot password
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from .models import Admin
from .tokens import admin_token_generator
from django.contrib.auth.hashers import make_password


# Admin Forgot Password Page
def admin_forgot_password(request):
    if request.method == "POST":
        email = request.POST.get('email')
        try:
            admin_user = Admin.objects.get(email=email)
        except Admin.DoesNotExist:
            messages.error(request, "Email not registered.")
            return render(request, "admindashboard/admin_forgot_password.html")

        uid = urlsafe_base64_encode(force_bytes(admin_user.id))
        token = admin_token_generator.make_token(admin_user)
        reset_link = f"http://127.0.0.1:8000/admin-reset-password/{uid}/{token}/"

        
        subject = "Admin Password Reset"
        message = f"Click the link to reset your password:\n{reset_link}"
        send_mail(subject, message, settings.EMAIL_HOST_USER, [email], fail_silently=False)

        
        return render(request, "admindashboard/admin_forgot_password_done.html", {"email": email})

    return render(request, "admindashboard/admin_forgot_password.html")

# Admin Reset Password Page
def admin_reset_password(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        admin_user = Admin.objects.get(id=uid)
    except (Admin.DoesNotExist, ValueError, TypeError):
        admin_user = None

    if admin_user is not None and admin_token_generator.check_token(admin_user, token):
        if request.method == "POST":
            password = request.POST.get("password")
            confirm_password = request.POST.get("confirm_password")

            if password != confirm_password:
                messages.error(request, "Passwords do not match.")
                return render(request, "admindashboard/admin_reset_password.html")

            admin_user.password = make_password(password)  
            admin_user.save()
            
            request.session['admin_id'] = admin_user.id
            messages.success(request, "")
            return redirect("admindashboard")  

        return render(request, "admindashboard/admin_reset_password.html")
    else:
        messages.error(request, "Invalid or expired reset link.")
        return redirect("admin_forgot_password")  

# Admin reset confirmation page
def admin_reset_confirmation(request):
    return render(request, 'admindashboard/admin_reset_confirmation.html')



from django.shortcuts import render, redirect
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from .models import Admin  

def admin_reset_confirm(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        admin = Admin.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Admin.DoesNotExist):
        admin = None

    if admin is not None and admin_token_generator.check_token(admin, token):
        if request.method == "POST":
            new_password = request.POST.get("password")
            confirm_password = request.POST.get("confirm_password")
            if new_password == confirm_password:
                admin.password = make_password(new_password)
                admin.save()
                messages.success(request, " Password reset successful! Please login with your new password.")
                return redirect("admindashboard")  
            else:
                messages.error(request, " Passwords do not match.")
        return render(request, "admindashboard/admin_reset_confirm.html", {"uidb64": uidb64, "token": token})
    else:
        messages.error(request, " Reset link is invalid or expired.")
        return redirect("admin_forgot_password")



from django.contrib.auth.hashers import make_password
from main.models import Admin   

def reset_admin_password(email, new_password):
    try:
        admin = Admin.objects.get(email=email)   
        admin.password = make_password(new_password)  
        admin.save(update_fields=['password'])
        print(" Password update ho gaya")
    except Admin.DoesNotExist:
        print(" Ye email database me exist hi nahi karta")


import hashlib, time
from django.conf import settings

def generate_reset_token(email):
    timestamp = str(int(time.time()))
    raw = email + timestamp + settings.SECRET_KEY
    token = hashlib.sha256(raw.encode()).hexdigest()
    return token, timestamp

def verify_reset_token(email, token, timestamp, expiry=3600):
    raw = email + timestamp + settings.SECRET_KEY
    expected_token = hashlib.sha256(raw.encode()).hexdigest()
   
    return token == expected_token and (int(time.time()) - int(timestamp)) < expiry


from django.contrib.auth.tokens import PasswordResetTokenGenerator


class AdminTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, admin, timestamp):
       
        return str(admin.pk) + str(timestamp)

admin_token_generator = AdminTokenGenerator()



from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from .models import Customer, Seller
from django.shortcuts import redirect, render
from .models import Seller


#seller forget password

def seller_forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            seller = Seller.objects.get(email=email)
        except Seller.DoesNotExist:
            messages.error(request, "Email not registered.")
            return render(request, "seldashboard/seller_forgot_password.html")

        uid = urlsafe_base64_encode(force_bytes(seller.pk))
        token = seller_token_generator.make_token(seller)
        reset_link = f"http://127.0.0.1:8000/seller-reset/{uid}/{token}/"
        
        all_sellers_emails = list(Seller.objects.values_list("email", flat=True))

       
        send_mail(
         subject="Seller Password Reset",
         message=f"Hello {seller.name},\n\nClick the link to reset your password:\n{reset_link}",
         from_email=settings.EMAIL_HOST_USER,
         recipient_list=[seller.email],   
         fail_silently=False,
          )


        return render(request, "seldashboard/seller_password_reset_done.html")
    return render(request, "seldashboard/seller_forgot_password.html")

from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.hashers import make_password

def seller_reset_password(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        seller = Seller.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Seller.DoesNotExist):
        messages.error(request, "Invalid link.")
        return redirect("seller_forgot_password")

    if seller_token_generator.check_token(seller, token):
        if request.method == "POST":
            password = request.POST.get("password")
            seller.password = make_password(password)
            seller.save()
            messages.success(request, "Password reset successful.")
            return redirect("sellerlogin")
        return render(request, "seldashboard/seller_reset_confirm.html")
    else:
        messages.error(request, "Link expired or invalid.")
        return redirect("seller_forgot_password")

   
def seller_reset_password_done(request):
    return render(request, 'seldashboard/seller_reset_password_done.html')




from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.shortcuts import render, redirect, get_object_or_404
from .models import Customer  
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from .tokens import customer_token_generator  
from django.contrib.auth.tokens import PasswordResetTokenGenerator

class SellerTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, seller, timestamp):
      
        return str(seller.pk) + str(timestamp)

seller_token_generator = SellerTokenGenerator()


#cust forget password

def customer_forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            customer = Customer.objects.get(email=email)
        except Customer.DoesNotExist:
            messages.error(request, "This email is not registered.")
            return redirect( 'forgot_password_done')

      
        uid = urlsafe_base64_encode(force_bytes(customer.pk))
        token = customer_token_generator.make_token(customer)
        reset_link = request.build_absolute_uri(
            f"/customer-reset-password/{uid}/{token}/"
        )

        
        send_mail(
            "Reset Your Password",
            f"Click the link to reset your password: {reset_link}",
            "admin@craftoria.com",
            [customer.email],
            fail_silently=False,
        )

       
        return redirect("forgot_password_done")

    return render(request, "customer/forgot_password.html")


from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login

def customer_reset_password(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        customer = Customer.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Customer.DoesNotExist):
        customer = None

    if customer and customer_token_generator.check_token(customer, token):
        if request.method == "POST":
            new_password = request.POST.get("password")
            customer.password = make_password(new_password)
            customer.save()

            
            user = authenticate(request, email=customer.email, password=new_password)
            if user is not None:
                login(request, user)  
                messages.success(request, "Password reset successful. You are now logged in.")
                return redirect("customerdashboard")  

            messages.success(request, "Password reset successful. Please log in.")
            return redirect("custlogin")

       
        return render(request, "customer/reset_password.html")
    else:
        messages.error(request, "Invalid or expired link.")
        return redirect("customer_forgot_password")


from django.shortcuts import render
def customer_password_reset_done(request):
    return render(request, "customer/password_reset_done.html")

def customer_forgot_password_done(request):
    return render(request, "customer/forgot_password_done.html")

def adminnotification(request):
    return render(request, 'admindashboard/adminnotification.html')                      

from django.shortcuts import render

def sellnotification(request):
    return render(request, 'seldashboard/sellnotification.html')
