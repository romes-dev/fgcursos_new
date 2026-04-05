from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.cart.cart import Cart
from .models import Order, OrderItem
from .forms import CheckoutForm


@login_required
def checkout_view(request):
    cart = Cart(request)

    if not cart:
        messages.warning(request, 'Seu carrinho está vazio.')
        return redirect('cart:detail')

    user = request.user
    profile = getattr(user, 'profile', None)

    initial = {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'phone': profile.phone if profile else '',
        'cpf': profile.cpf if profile else '',
    }

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            subtotal = cart.total
            order = Order.objects.create(
                user=user,
                customer_name=f"{form.cleaned_data['first_name']} {form.cleaned_data['last_name']}",
                customer_email=form.cleaned_data['email'],
                customer_phone=form.cleaned_data.get('phone', ''),
                customer_cpf=form.cleaned_data.get('cpf', ''),
                subtotal=subtotal,
                total=subtotal,
            )

            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    course=item['course'],
                    course_title=item['course'].title,
                    unit_price=item['price'],
                    total_price=item['price'],
                )

            cart.clear()
            return redirect('payments:create', order_number=order.number)
    else:
        form = CheckoutForm(initial=initial)

    return render(request, 'cart/checkout.html', {'form': form, 'cart': cart})


@login_required
def order_detail_view(request, number):
    order = get_object_or_404(Order, number=number, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})
