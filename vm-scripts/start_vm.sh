#!/bin/bash

VM_NAME=$1
# ARGUMENT 2 (le port de la DB) EST IGNORÉ
PROXY_LISTEN_PORT=$3
PROXY_LISTEN_HOST=$4

SERVER_IP=$(hostname -I | awk '{print $1}')

# --- Logique de démarrage ---
VM_STATE=$(virsh domstate $VM_NAME 2>/dev/null)

if [ "$VM_STATE" == "shut off" ]; then
    echo "VM is shut off. Starting..."
    virsh start $VM_NAME
    # PAUSE CRUCIALE: On attend 3s que le processus de la VM s'initialise
    sleep 3
elif [ "$VM_STATE" == "running" ]; then
    echo "VM is already running. Proceeding..."
else
    echo "Error: Cannot determine VM state for '$VM_NAME'. Does it exist?"
    exit 1
fi

# --- Découverte du port (APRÈS s'être assuré que la VM est lancée) ---
echo "Discovering VNC port for VM '$VM_NAME'..."
VNC_DISPLAY=$(virsh vncdisplay $VM_NAME 2>/dev/null)

if [ -z "$VNC_DISPLAY" ]; then
    echo "Error: Could not get VNC display for VM '$VM_NAME'. The VM might have failed to start its graphics component."
    exit 1
fi

DISPLAY_NUM=$(echo $VNC_DISPLAY | cut -d: -f2)
VM_VNC_PORT=$((5900 + DISPLAY_NUM))
echo "VNC port discovered: $VM_VNC_PORT"
# --- Fin de la découverte ---

# Le reste du script est inchangé
echo "Waiting for VM's VNC port $SERVER_IP:$VM_VNC_PORT to be active..."
for i in {1..180}; do
    if nc -z $SERVER_IP $VM_VNC_PORT; then
        echo "VNC port is active."
        break
    fi
    sleep 1
done

if ! nc -z $SERVER_IP $VM_VNC_PORT; then
    echo "Error: VNC port did not become active in 180 seconds."
    exit 1
fi

echo "Starting noVNC proxy targeting $SERVER_IP:$VM_VNC_PORT"
nohup /opt/noVNC/utils/novnc_proxy \
    --vnc $SERVER_IP:$VM_VNC_PORT \
    --listen $PROXY_LISTEN_HOST:$PROXY_LISTEN_PORT > /tmp/proxy-$VM_NAME.log 2>&1 &

echo "Proxy started successfully."
