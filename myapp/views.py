from django.contrib.auth.decorators import login_required  # Add this line
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate
from .forms import UserRegisterForm
from django.contrib import messages
from .models import Book, CartItem, Order


# Your other views follow

def catalog(request):
    books = Book.objects.all()
    return render(request, 'myapp/catalog.html', {'books': books})

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # Хэшируем пароль
            user.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Аккаунт создан для {username}!')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_superuser:
                    messages.error(request, 'Суперпользователи не могут заходить через эту форму.')
                    return redirect('login')
                login(request, user)
                messages.success(request, f'Добро пожаловать, {username}!')
                return redirect('catalog')
            else:
                messages.error(request, 'Неверный логин или пароль.')
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})


def school(request):
    return render(request, 'myapp/school.html')

def discount(request):
    return render(request, 'myapp/discount.html')

def read(request):
    return render(request, 'myapp/read.html')

def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    return render(request, 'myapp/book1.html', {'book': book})

@login_required
def cart_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    cart_total = sum(item.total_price for item in cart_items)
    return render(request, 'myapp/cart.html', {'cart_items': cart_items, 'cart_total': cart_total})

def add_to_cart(request, book_id):
    if request.method == 'POST':
        book = get_object_or_404(Book, id=book_id)
        cart = request.session.get('cart', {})
        cart[book_id] = cart.get(book_id, 0) + 1
        request.session['cart'] = cart
        return redirect('cart_view')

@login_required
def remove_from_cart(request, book_id):
    cart_item = CartItem.objects.filter(user=request.user, book_id=book_id).first()
    if cart_item:
        cart_item.delete()
    return redirect('cart_view')

@login_required
def checkout_view(request):
    # Проверяем, есть ли товары в корзине
    cart_items = CartItem.objects.filter(user=request.user)
    if not cart_items:
        return redirect('cart')

    cart_total = sum(item.total_price for item in cart_items)

    if request.method == 'POST':
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        payment_method = request.POST.get('payment_method')

        # Создаем новый заказ
        order = Order.objects.create(
            user=request.user,
            total_amount=cart_total,
            address=address,
            phone=phone,
            payment_method=payment_method
        )

        # Добавляем товары из корзины в заказ
        for item in cart_items:
            order.cart_items.add(item)

        # Очищаем корзину
        cart_items.delete()

        # Сообщение для пользователя
        messages.success(request, 'Молодец! Ваш заказ принят на обработку.')
        return redirect('order_confirmation')  # Перенаправление на страницу подтверждения заказа

    return render(request, 'myapp/checkout.html', {'cart_items': cart_items, 'cart_total': cart_total})

@login_required
def order_confirmation(request):
    # Получаем последний заказ пользователя
    last_order = Order.objects.filter(user=request.user).last()
    return render(request, 'order_confirmation.html', {'order': last_order})
