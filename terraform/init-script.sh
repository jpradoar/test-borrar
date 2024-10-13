#!/bin/bash
sudo apt-get update > /dev/null
sudo apt-get install -y wget curl nano snapd git kubecolor awscli  > /dev/null
sudo snap install microk8s --classic  > /dev/null
sudo snap install kubectl --classic  > /dev/null
#mkdir -p  ~/.kube
#sudo usermod -a -G microk8s $USER
#sudo chown -f -R $USER ~/.kube
mkdir -p /home/admin/.kube
sudo usermod -a -G microk8s admin
chown -R admin:admin /home/admin/.kube
newgrp microk8s
microk8s start
microk8s status --wait-ready
microk8s enable hostpath-storage
microk8s enable storage
#microk8s config  > ~/.kube/config
sudo chown -R admin:admin /home/admin/.kube
microk8s config  > /home/admin/.kube/config
echo 'alias kubectl="kubecolor"' >> /home/admin/.bashrc
echo 'alias ll="ls -lha"' >> /home/admin/.bashrc
# echo 'alias kubectl="microk8s kubectl"' >>  .bashrc
#microk8s status
kubectl get pod -A