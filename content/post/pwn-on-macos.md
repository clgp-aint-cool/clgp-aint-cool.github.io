---
title: 'Pwn on MacOS'
author: clgp
date: '2025-11-14T00:49:18+07:00'
categories:
  - ctf 
tags:
  - tutorial
---

## The Issue

Pwn or reverse engineering, especially running ELF/x86 files on macOS (M series), can be frustrating. But I finally found a solid solution!

## Why Docker?

Instead of using a VM, Docker is a better tools for me : 

- ✅ Work directly on macos terminal (I use Iterm2)
- ✅ Lightweight and fast (though running through qemu)
- ✅ Access the same directory as your host

## Solution

I found this [pwntainer](https://github.com/1ikeadragon/pwntainer) which provides an excellent solution for this exact issue.

### Installation Steps

First, install the required tools:

```bash
brew install docker
brew install colima
brew install docker-buildx
```

### Start Colima with x86_64 Architecture

```bash
colima start -p x64 -a x86_64 -c 8 -m 4 -d 10 --vm-type qemu
```

This tells Colima to boot a Linux VM with x86_64 architecture. Once running, it starts the Docker engine inside it. Colima automatically configures your Docker CLI to point to this new VM.

### Build and Run Docker Container

```bash
docker buildx -t pwn:pwn .
docker run --security-opt seccomp=unconfined --privileged --cap-add=SYS_PTRACE -p 31337:31337 -v ./:/pwn -it pwn:pwn bash
```

## Network Issues & Fix

When I first set this up, Docker constantly failed fetching packages via apt-get on bad networks. The solution was simple: modify the Dockerfile by adding a line under the `FROM` instruction:

```dockerfile
COPY ./badproxy /etc/apt/apt.conf.d/99fixbadproxy
```

The `badproxy` file content should look like this:

```
Acquire::http::Pipeline-Depth 0;
Acquire::http::No-Cache true;
Acquire::BrokenProxy    true;
```

With this single modification, the Docker setup runs flawlessly and is ready to use! 
<img src = "/images/speed.jpeg">
