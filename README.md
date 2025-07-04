# ☁️ CloudOS – Cloud-Based IaaS for Browser-Based VM Access

CloudOS is a cloud-based IaaS (Infrastructure as a Service) web platform that allows users to create, configure, and access virtual machines directly from their browser. It requires no hardware or local resources — just an internet connection. Users can launch isolated Ubuntu VMs remotely in a few clicks.

> 🔥 Built with Django, QEMU/KVM, noVNC, and cloud-init.

---

## 🚀 Features

- ✅ User registration and authentication
- ✅ Ubuntu 24.04 VM deployment
- ✅ Resource customization (CPU, RAM, Disk)
- ✅ VMs launched via QEMU/KVM and `virsh`
- ✅ Cloud-init automation for user setup and isolation
- ✅ Web-based remote desktop access using noVNC
- ✅ Secure cloning from base image (per-user VMs)
- ✅ Local network access tested (LAN deployment)
- 🛠️ Multi-OS support (planned)
- 🛠️ Full dashboard functionalities (planned)
- 🛠️ Admin interface (planned)

---

## 🧱 Architecture

| Component     | Stack / Tool                          |
|---------------|----------------------------------------|
| **Server**    | NGINX                                  |
| **Backend**   | Django (Python)                        |
| **Frontend**  | Django Templating Engine, HTML, Bootstrap |
| **Database**  | MySQL                                  |
| **VM Engine** | QEMU/KVM with `virsh`                  |
| **Automation**| `cloud-init`                           |
| **Remote Access** | noVNC                             |
| **Scripts**   | Bash: `create_vm.sh`, `start_vm.sh`    |

---

## 🖥️ Deployment

CloudOS was tested in a **local network setup**, with successful VM creation and browser-based access from:
- Phones
- Laptops
- Other machines within the same LAN

> Deployment to a public server or cloud host is possible with proper port forwarding and system-level configuration (not tested yet).

### ✅ Client Requirements
- Any modern browser
- Stable internet connection

---

## 🔐 Security

- VMs are fully cloned per user using base images.
- `cloud-init` ensures that cloned VMs:
  - Remove default users
  - Create only the registered user account
- VMs are isolated from one another.

---

## 📸 Demo

👉 **Screenshots** and a **6-minute video demo** available soon (including full process: registration → VM launch).

---

## 🎯 Motivation

> _“I have a low-end PC and couldn’t launch big software or isolated labs. CloudOS is my solution — a scalable way to run cloud-hosted VMs from anywhere, using only a browser.”_

This project was a personal challenge to learn:
- Virtualization with KVM/QEMU
- VM automation and orchestration
- Full-stack web development using Django
- System scripting and real-world IaaS concepts

---

## 🛠️ Future Plans

- [ ] Add more Linux distros (Debian, Kali, etc.)
- [ ] Improve dashboard with fully functional buttons
- [ ] Add VM networking features (e.g., SSH access)
- [ ] Implement admin panel for monitoring and control
- [ ] Polish frontend and UI/UX
- [ ] Deploy on a public VPS or cloud provider

---

## 📁 Scripts

Located in `vm-scripts/`:

- `create_vm.sh`: Automates VM image creation
- `start_vm.sh`: Starts VM and prepares noVNC access

---

## 📣 Contributions

This project is currently in early-stage development and not production-ready. If you'd like to contribute ideas, improvements, or bug fixes, feel free to open an issue or fork the repo!

---

## ⚖️ License

MIT License — free to use, modify, and distribute.

---

> Made with 💻 by [Rayane](https://github.com/Rayanex7)
