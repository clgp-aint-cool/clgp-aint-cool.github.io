---
title: 'Building an Enterprise-Grade Private Cloud with Proxmox VE'
author: clgp
date: '2026-06-18T19:13:33+07:00'
categories:
  - Infrastructure
  - Homelab
tags:
  - Proxmox
  - Nextcloud
  - ZFS
  - Self-Hosted
  - VPN
---

## Overview

In this project, I designed and deployed a secured private cloud infrastructure. The setup uses Proxmox VE as the hypervisor foundation, Nextcloud for cloud storage, and various security layers including SSL encryption and VPN access.

## Challenge: Router AP Isolation

My home WiFi router enforces **AP isolation**, preventing devices on the network from communicating with each other. This posed a significant challenge for accessing the Proxmox dashboard and managing the infrastructure.

**Solution**: I deployed **Tailscale** to create a secure VPN mesh network, enabling direct access to the Proxmox host and all hosted services without modifying router settings or exposing services to the public internet.

## Architecture

```
Internet
   │
   └──> Tailscale VPN ──> Proxmox VE (KVM Hypervisor)
                              │
                              ├──> Ubuntu VM/LXC: Nextcloud
                              │    └──> Nginx Reverse Proxy
                              │         └──> Let's Encrypt SSL
                              │
                              └──> ZFS Storage Pool (Compression + Snapshots)
```

## Implementation Steps 
Note : all the script are taken from https://community-scripts.org
### 1. Proxmox VE Installation & Configuration

- Installed **Proxmox VE** bare-metal hypervisor on dedicated hardware
- Set up network bridge for VM connectivity 
- Configured resource allocation pools (CPU, RAM, storage)

### 2. Tailscale VPN Setup

Due to AP isolation on my router:

```bash
# Install Tailscale on Proxmox host
curl -fsSL https://tailscale.com/install.sh | sh
tailscale up
```

- Created a Tailscale network and authenticated the Proxmox host
- Access Proxmox dashboard via Tailscale IP: `https://<tailscale-ip>:8006`
- All management tasks now routable through the secure VPN mesh

### 3. Nextcloud VM Provisioning

- Created Ubuntu LXC container within Proxmox 
- Configured database and initial admin account

### 4. Nginx Reverse Proxy & SSL

- Deployed **Nginx** as reverse proxy for Nextcloud
- Integrated **Let's Encrypt** for automatic SSL certificate provisioning
- Configured HTTPS enforcement and security headers


### 5. ZFS Storage Configuration

- Created **ZFS storage pool** for VM disks and Nextcloud data
- Enabled LZ4 compression for optimal disk I/O performance
- Configured automatic snapshots for data redundancy

```bash
# Create ZFS pool
zpool create -o ashift=12 tank /dev/sdb /dev/sdc

# Enable compression
zfs set compression=lz4 tank

# Configure automated snapshots
zfs snapshot tank@backup-$(date +%Y%m%d)
```

### 6. Backup & Disaster Recovery

- Configured **Proxmox Backup Server** integration
- Set up automated VM/LXC backup schedules (daily/weekly)
- Implemented snapshot retention policies
- Tested disaster recovery procedures

```bash
# Proxmox backup job (configured via web UI or CLI)
vzdump <vmid> --storage local-zfs --mode snapshot --compress lzo
```

## Technologies Used

- **Proxmox VE** (KVM hypervisor)
- **Tailscale** (WireGuard-based VPN)
- **Nextcloud** (Private cloud storage)
- **Nginx** (Reverse proxy)
- **Let's Encrypt** (SSL certificates)
- **ZFS** (Advanced filesystem with compression and snapshots)
- **Linux** (Ubuntu LXC containers)


## Demo demonstration
---
