from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string
from cart.cart import Cart
from .models import Order, OrderItem
from .forms import OrderCreateForm
from .tasks import order_created
import weasyprint


def order_create(request):

    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)

        if form.is_valid():
            order = form.save(commit=False)
            if cart.coupon:
                order.coupon = cart.coupon
                order.discount = cart.coupon.discount
            order.save()
            
            for item in cart:
                OrderItem.objects.create(order=order, product=item['product'],
                    price=item['price'], quantity=item['quantity'])
            
            cart.clear()
            order_created.delay(order.id) # launch asyncronous task
            request.session['order_id'] = order.id # set the order in the session

            return redirect(reverse('payment:process')) # redirect for payment
    else:
        form = OrderCreateForm()
    
    return render(request, 'orders/order/create.html', {'form': form})


@staff_member_required
def admin_order_detail(request, order_id):

    order = get_object_or_404(Order, id=order_id)

    return render(request, 
        'admin/orders/order/detail.html', {'order': order})


@staff_member_required
def admin_order_pdf(request, order_id):

    order = get_object_or_404(Order, id=order_id)
    html = render_to_string('admin/orders/order/pdf.html', {'order': order})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=order_{order.id}.pdf'

    weasyprint.HTML(string=html).write_pdf(response,
        stylesheets=[weasyprint.CSS(
            settings.STATIC_ROOT + 'css/pdf.css')])

    return response
