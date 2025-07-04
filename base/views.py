from django.shortcuts import render, redirect
from base.models import VMConfig, VMInstance
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.contrib import messages
import subprocess
from django.utils import timezone
import socket
from .utils import get_free_port

# Create your views here.

ISO_PATH = "/home/rayane/ISO/ubuntu-24.04.2-desktop-amd64.iso"


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

def vm_status(request):
    command = subprocess.run(f"sudo virsh list --all | grep {request.user.username}", shell=True, capture_output=True, text=True)
    output = command.stdout.strip()
    print("output:", output)
    if not output:
        return None
    parts = output.split()
    if len(parts) < 3:
        return None
    VmStat = {
        "id":parts[0],
        "name": parts[1],
        "status": " ".join(parts[2:])
    }
    if VmStat["status"]:
        return VmStat["status"]
    return "stopped"


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

            vm_config = VMConfig.objects.filter(client=request.user).first()
            VMInstance.objects.create(
                client=request.user,
                config=vm_config,
                vm_name=f"{username}",
                status='shut off',
                ip_address=None,
                created_at=timezone.now(),
                last_used_at=timezone.now()
            )

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
    print("Starting VM...")
    if request.method == 'GET':
        vm_name = request.user.username
        vm_config = VMConfig.objects.get(client=request.user)

        # Port VNC interne de la VM (ex: 5901, 5902...)
        vm_vnc_port = vm_config.port

        # Port sur lequel le PROXY noVNC va écouter (ex: 6080, 6081...)
        proxy_listen_port = get_free_port()

        # Le proxy doit écouter sur localhost pour n'être accessible que par Nginx
        proxy_listen_host = "127.0.0.1"

        print(f"VM: {vm_name}, VM VNC Port: {vm_vnc_port}, Proxy Listen Port: {proxy_listen_port}")

        # --- CHANGEMENT ---
        # On passe maintenant 4 arguments au script shell, y compris l'hôte d'écoute du proxy
        command = subprocess.run(
            ["sudo", "/home/rayane/vm-scripts/start_vm.sh", vm_name, str(vm_vnc_port), str(proxy_listen_port), proxy_listen_host],
            check=True,
            capture_output=True,
            text=True
        )

        VMInstance.objects.filter(client=request.user).update(status=vm_status(request), last_used_at=timezone.now())
        command_output = command.stdout.strip()
        print(f"Command output: {command_output}")

        # --- CHANGEMENT MAJEUR ---
        # On prépare le contexte pour le template avec les bonnes informations
        context = {
            # On utilise request.get_host() pour obtenir dynamiquement "CloudOS.ma"
            'vnc_host': request.get_host(),

            # C'est le port du proxy, qui sera utilisé dans l'URL pour Nginx
            'vnc_port': proxy_listen_port,

            # On détermine le protocole (ws pour http, wss pour https)
            'vnc_protocol': 'wss' if request.is_secure() else 'ws',
        }
        return render(request, 'novnc_viewer.html', context)