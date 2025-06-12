# Option 1: Use settings.AUTH_USER_MODEL for both (RECOMMENDED)
from django.db import models
from django.conf import settings

class VMConfig(models.Model):
    name = models.CharField(max_length=100)
    ram_mb = models.IntegerField()
    cpu_cores = models.IntegerField()
    disk_gb = models.IntegerField()
    os_type = models.CharField(max_length=50)
    port = models.IntegerField()
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

class VMInstance(models.Model):
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    config = models.ForeignKey(VMConfig, on_delete=models.SET_NULL, null=True)
    vm_name = models.CharField(max_length=100)
    status = models.CharField(
        max_length=10,
        choices=[
            ('running', 'running'),
            ('stopped', 'stopped'),
            ('paused', 'paused')
        ],
        default='stopped'
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
