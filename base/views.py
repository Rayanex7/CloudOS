from django.shortcuts import render, redirect
from base.models import VMConfig, VMInstance
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.contrib import messages
import subprocess
import os
import pwd
import socket

# Create your views here.

ISO_PATH = "/home/rayane/ISO/ubuntu-24.04.2-desktop-amd64.iso"

def getvnc_port():
    used_ports = subprocess.run(["sudo", "ss -tuln | awk '$4 ~ /:([6][0-9][8-9][0-9])|([6][9][0-9][0-9])$/' | awk -F':' '{print $NF}'"], shell=True)
    if used_ports == None:
        return 6080
    else:
        for i in range(6080, 6100):
            if str(i) not in used_ports.stdout:
                return i
    return None

def home(request):
    return render(request, 'home.html', {'user':request.user})

def help(request):
    return render(request, 'Support.html')

def dashboard(request):
    if request.method == 'POST':
        pass
    return render(request, 'dashboard.html')

def os_library(request):
    os_images = [
        {"name": "Windows", "img": "Windows_logo.png"},
        {"name": "Windows Server", "img": "R.png"},
        {"name": "Ubuntu", "img": "U.png"},
        {"name": "Kali Linux", "img": "K.png"},
    ]
    return render(request, 'os_library.html', {'os_images': os_images})

@csrf_protect
@login_required
def Save_vm(request):
    if request.method == 'POST':
        os_name = request.POST.get('os_name')
        cpu = request.POST.get('cpu')
        ram = request.POST.get('ram')
        storage = request.POST.get('storage')
        username = request.user.username
        vmpass = request.POST.get('vmpass')
        cmd = ["sudo", "/home/rayane/vm-scripts/create_vm.sh", username, vmpass, storage, ram, cpu]
        vm_status = subprocess.run(["sudo", "virsh", "list", "--all"], capture_output=True, text=True)

        try:
            print("command Started")
            command = subprocess.run(
                cmd,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
                )
            vnc_port = command.stdout.strip()
            print(f"Command output: {vnc_port}")
            print(f"Command stderr: {command.stderr}")
            print("Command finished")

        except subprocess.CalledProcessError as e:
            print(f"Command failed: {e}")
            print(f"Return code: {e.returncode}")
            print(f"stdout: {e.stdout}")
            print(f"stderr: {e.stderr}")
            return JsonResponse({"status": "error", "message": e.stderr.strip()}, status=500)
        try:
            VMConfig.objects.create(
                name=os_name,
                ram_mb=ram,
                cpu_cores=cpu,
                disk_gb=storage,
                os_type=os_name,
                port=vnc_port,
                client=request.user
            )

            VMInstance.objects.create(
                client=request.user,
                config=VMConfig.objects.filter(client=request.user).values_list('id', flat=True).first(),
                vm_name=f"{username}-vm",
            
            messages.success(request, f"VM {username}-vm created successfully")
            print("VMConfig saved successfully")
            return redirect('base:os_library')
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    return render(request, 'os_library.html')

def profile(request):
        if request.method == 'POST':
            username = request.POST.get('username')
            email = request.POST.get('email')
            updated_password = request.POST.get('new_password')
            try:
                user = User.objects.get(username=username, email=email, id=request.user.id)
                user.set_password(updated_password)
                user.save()
                message = "Password updated successfully"
                logout(request)
                return redirect('authentication:login')
            except User.DoesNotExist:
                message = "User does not exist"
            return render(request, 'profile.html', {'message':message})
        user_id = request.user.id
        UserVm = VMConfig.objects.filter(client=user_id)
        user_vms = list(UserVm.values())
        return render(request, 'profile.html', {"user_vms": user_vms})

def start_vm(request):
    if request.method == 'GET':        
        vm_name = request.user.username + "-vm"
        vm_port = VMConfig.objects.get(client=request.user.username).port
        vnc_port = getvnc_port()
        vnc_host = socket.gethostbyname(socket.gethostname())

        subprocess.run(["sudo", "/home/rayane/vm-scripts/start_vm.sh", vm_name, vm_port, vnc_port], check=True)
        
        context = {
            'vnc_host': vnc_host,
            'vnc_port': vnc_port,
        }
        return render(request, 'novnc_viewer.html', context)


    












