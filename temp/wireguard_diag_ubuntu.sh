#!/bin/bash

echo "=== Full WireGuard Diagnostics Script ==="
echo "Running as user: $(whoami)"
echo "========================================="
echo ""

# Проверка ОС
echo "1. Checking OS and Version:"
OS=$(grep '^NAME=' /etc/os-release | cut -d= -f2 | tr -d '"')
VERSION=$(grep '^VERSION_ID=' /etc/os-release | cut -d= -f2 | tr -d '"')
echo "Operating System: $OS"
echo "Version: $VERSION"
echo ""

# Проверка состояния WireGuard
echo "2. Checking WireGuard Status:"
if command -v wg >/dev/null 2>&1; then
    echo "WireGuard is installed."
    echo "WireGuard Interfaces:"
    sudo wg show
else
    echo "WireGuard is NOT installed."
    exit 1
fi
echo ""

# Проверка сетевых маршрутов
echo "3. Checking Network Routes:"
ip route
echo ""

# Проверка IP-адресов
echo "4. Checking IP Addresses:"
ip addr
echo ""

# Проверка форвардинга пакетов
echo "5. Checking IP Forwarding:"
sudo sysctl net.ipv4.ip_forward
sudo sysctl net.ipv6.conf.all.forwarding
echo ""

# Проверка MTU
echo "6. Checking MTU:"
for iface in $(ip link show | grep wg | awk -F: '{print $2}' | tr -d ' '); do
    echo "MTU for $iface:"
    ip link show $iface | grep mtu
done
echo ""

# Проверка фаервола
echo "7. Checking Firewall Rules:"
if command -v ufw >/dev/null 2>&1; then
    echo "UFW Status:"
    sudo ufw status verbose
else
    echo "UFW is not installed."
fi

echo ""
echo "iptables Rules:"
sudo iptables -L -v -n
echo ""

# Диагностика трафика
echo "8. Capturing WireGuard Traffic (10 packets per interface):"
if [ "$(ip link show | grep wg | wc -l)" -eq 0 ]; then
    echo "No WireGuard interfaces found."
else
    for iface in $(ip link show | grep wg | awk -F: '{print $2}' | tr -d ' '); do
        echo "Capturing traffic on $iface:"
        sudo tcpdump -i $iface -c 10 -n &
        sleep 5
    done
fi
echo ""

# Тестирование ICMP
echo "9. Testing ICMP Ping:"
read -p "Enter the IP of the remote peer to ping: " remote_ip
if [ -z "$remote_ip" ]; then
    echo "No IP provided. Skipping ping test."
else
    echo "Pinging $remote_ip..."
    ping -c 4 $remote_ip
fi
echo ""

echo "=== Diagnostics Completed ==="
