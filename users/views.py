from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
from django import forms
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required
from users.models import UserProfile, Wishlist
from products.models import Product, Category, SubCategory, Review
from django.core.mail import send_mail
from .tokens import account_activation_token


# User Profile Update Form
class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['delivery_address', 'phone_number']


# User Registration View
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            UserProfile.objects.create(user=user, delivery_address=request.POST['delivery_address'])

            # Send verification email
            current_site = get_current_site(request)
            subject = 'Activate Your Account'
            message = render_to_string('users/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            send_mail(subject, message, 'from@example.com', [user.email])
            return redirect('account_activation_sent')
    else:
        form = UserCreationForm()
    return render(request, 'users/register.html', {'form': form})


# View for Updating User Profile
@login_required
def update_profile(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = UserProfileUpdateForm(instance=user_profile)
    return render(request, 'users/update_profile.html', {'form': form, 'user_profile': user_profile})


# Login View
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('users:dashboard')
        else:
            return render(request, 'users/login.html', {'error': 'Invalid username or password'})
    return render(request, 'users/login.html')


# Logout View
def logout_view(request):
    logout(request)
    return redirect('index')


# Account Activation Sent View
def account_activation_sent(request):
    return render(request, 'users/account_activation_sent.html')


# Account Activation View
def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('dashboard')
    else:
        return render(request, 'users/account_activation_invalid.html')


# Add to Wishlist View
@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    if created:
        wishlist_item.save()
    return redirect('product_detail', product_id=product_id)


@login_required
def dashboard(request):
    return render(request, 'users/dashboard.html')


def send_account_activation_email(user, request):
    current_site = get_current_site(request)
    mail_subject = 'Activate your account.'
    message = render_to_string('users/account_activation_email.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http',
    })
    send_mail(
        mail_subject,
        message,
        'test@example.com',  # Sender email
        [user.email],
        fail_silently=False,
    )


def activate(request, uidb64, token):
    # Get the User model dynamically
    User = get_user_model()

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Your account has been activated successfully!')
        return redirect('users:login')
    else:
        messages.error(request, 'Activation link is invalid!')
        return render(request, 'users/account_activation_invalid.html')
