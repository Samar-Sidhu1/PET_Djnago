from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.urls import reverse
from datetime import datetime
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Pet, AdoptionApplication, AdoptionRequest
from .models import User

def home(request):
    return render(request, 'home.html')

def pets(request):
    return render(request, 'pet_profile.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def privacy(request):
    return render(request, 'privacy_policy.html')

def terms(request):
    return render(request, 'terms_servises.html')

def pet_profile(request):
    species = request.GET.get('species')
    age = request.GET.get('age')
    search = request.GET.get('search')

    pets = Pet.objects.filter(is_available=True)

    if species:
        pets = pets.filter(species=species)
    if age:
        pets = pets.filter(age=age)
    if search:
        pets = pets.filter(name__icontains=search) | pets.filter(description__icontains=search)

    return render(request, 'pet_profile.html', {'pets': pets})

@require_http_methods(["GET"])
def get_pet_details(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
    return JsonResponse({
        'id': pet.id,
        'name': pet.name,
        'species': pet.get_species_display(),
        'breed': pet.breed,
        'age': pet.get_age_display(),
        'gender': pet.get_gender_display(),
        'description': pet.description,
        'image_url': pet.image.url if pet.image else None,
    })

@require_http_methods(["POST"])
def submit_adoption(request):
    try:
        adoption = AdoptionRequest.objects.create(
            pet_id=request.POST.get('pet_id'),
            name=request.POST.get('name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone'),
            address=request.POST.get('address'),
            reason=request.POST.get('reason')
        )
        return JsonResponse({'success': True, 'id': adoption.id})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm = request.POST.get('confirm', '')

        # Validation checks
        if not all([username, email, password, confirm]):
            messages.error(request, "All fields are required")
            return render(request, 'register.html')

        if password != confirm:
            messages.error(request, "Passwords do not match")
            return render(request, 'register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return render(request, 'register.html')

        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, "Email already exists")
            return render(request, 'register.html')

        try:
            # Validate password strength
            validate_password(password)
            
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            
            # Send success message
            messages.success(request, 'Registration successful! Please login.')
            return redirect('login_user')

        except ValidationError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, "An error occurred during registration")
            
    return render(request, 'register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if not username or not password:
            messages.error(request, "Both username and password are required")
            return render(request, 'login.html')

        try:
            # Try to authenticate with username
            user = authenticate(request, username=username, password=password)
            
            if not user:
                # If username auth fails, try with email
                try:
                    user_obj = User.objects.get(email=username)
                    user = authenticate(request, username=user_obj.username, password=password)
                except User.DoesNotExist:
                    user = None

            if user is not None:
                if user.is_active:
                    login(request, user)
                    messages.success(request, f"Welcome back, {user.username}!")
                    return redirect('home')
                else:
                    messages.error(request, "Your account is disabled")
            else:
                messages.error(request, "Invalid username/email or password")
        except Exception as e:
            messages.error(request, "An error occurred during login")
            
    return render(request, 'login.html')

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have been successfully logged out")
    return redirect('home')