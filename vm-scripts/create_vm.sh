#!/bin/bash

USERNAME="$1"
RAW_PASSWORD="$2"
DISK_SIZE="$3"
RAM="$4"
VCPU="$5"

# Function to get a free VNC port
PORTNB() {
    USED_PORTS=$(ss -tuln | grep -oP ':[0-9]+' | cut -d: -f2 | sort -n | uniq)
    for ((port=5900; port<=5999; port++)); do
        if ! echo "$USED_PORTS" | grep -q "^$port$"; then
            echo "$port"
            return 0
        fi
    done
    echo "No free port found in range" >&2
    return 1
}

# Get a free VNC port
PORT=$(PORTNB) || exit 1

# Encrypt the password
ENC_PASSWORD=$(openssl passwd -6 "$RAW_PASSWORD")

# Generate user-data and meta-data
USERDATA=$(cat <<EOF
#cloud-config
hostname: ${USERNAME}-vm
users:
  - name: ${USERNAME}
    groups: sudo
    shell: /bin/bash
    sudo: ALL=(ALL) NOPASSWD:ALL
    lock_passwd: false
    passwd: "$ENC_PASSWORD"
chpasswd:
  expire: false
ssh_pwauth: true

growpart:
  mode: auto
  devices: ['/']
  ignore_growroot_disabled: false

resize_rootfs: true

runcmd:
  - userdel -r cleaner || true 
EOF
)

METADATA=$(cat <<EOF
instance-id: "${USERNAME}_vm"
local-hostname: "${USERNAME}_vm"
EOF
)

create_vm() {
    virsh net-start default 2>/dev/null

    mkdir -p "/var/lib/libvirt/images/$USERNAME/"
    echo "$USERDATA" > "/var/lib/libvirt/images/$USERNAME/user-data"
    echo "$METADATA" > "/var/lib/libvirt/images/$USERNAME/meta-data"

    genisoimage -output "/var/lib/libvirt/images/$USERNAME/seed.iso" \
      -volid cidata -joliet -rock \
      "/var/lib/libvirt/images/$USERNAME/user-data" \
      "/var/lib/libvirt/images/$USERNAME/meta-data" >&2

    qemu-img convert -f qcow2 -O qcow2 /var/lib/libvirt/images/base_ubuntu.qcow2 "/var/lib/libvirt/images/$USERNAME/$USERNAME.qcow2"
    qemu-img resize "/var/lib/libvirt/images/$USERNAME/$USERNAME.qcow2" $DISK_SIZE"G" >&2

    virt-install \
      --name "$USERNAME" \
      --memory "$RAM" \
      --vcpus "$VCPU" \
      --disk path="/var/lib/libvirt/images/$USERNAME/$USERNAME.qcow2",format=qcow2 \
      --disk path="/var/lib/libvirt/images/$USERNAME/seed.iso",device=cdrom \
      --os-type linux \
      --os-variant ubuntu20.04 \
      --graphics vnc,listen=0.0.0.0,port="$PORT" \
      --noautoconsole \
      --import \
      --network network=default \
      --noreboot > /dev/null 2>&1

    echo "$PORT"
}

create_vm

