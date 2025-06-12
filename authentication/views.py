from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, HttpResponse

def client_login(request):
    message = None
    if request.method == 'POST':
        action = request.POST.get('action_type')
        if action == 'login':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('base:home')
            message = "Invalid username or password"
        elif action == 'signup':
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            if User.objects.filter(username=username).exists():
                message = "Username already exists"
            else:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )
                user.save()
                message = "User created successfully"
        elif action == 'forgot_password':
            username = request.POST.get('username')
            if User.objects.filter(username=username).exists():
                message = "Password reset link sent to your email"
                return redirect('authentication:reset_password')
            else:
                message = "Username does not exist"
    return render(request, 'registration/login.html', {'message': message})

def logout_client(request):
    action = request.GET.get('action')
    if action == 'logout':
        logout(request)
        return redirect('base:home')