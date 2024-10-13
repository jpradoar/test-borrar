



# Levantar una EC2 e instalarle microk8s con el stack de monitoreo y mi stack de XaaS



### Create keys for Instance
	ssh-keygen -t rsa -b 4096 -f $PWD/demo_sshkey_tf



### Install and config MicroK8s
	sudo apt-get update
	sudo apt-get install -y wget curl nano snapd git kubecolor
	sudo snap install microk8s --classic
	sudo snap install kubectl --classic
	sudo microk8s status --wait-ready
	sudo microk8s enable storage
	sudo microk8s enable hostpath-storage
	sudo microk8s enable helm
	sudo usermod -a -G microk8s ubuntu	
	mkdir -p  ~/.kube
	sudo microk8s config > ~/.kube/config
	sudo chown -R ubuntu ~/.kube
	echo 'alias kubectl="kubecolor"' >>  .bashrc
	alias kubectl="kubecolor"
	kubectl get pod -A
	sudo microk8s status


### Install helm on local machine
	curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
	chmod 700 get_helm.sh
	./get_helm.sh



### mi SaaS Stack
git clone https://github.com/jpradoar/event-driven-architecture.git
cd event-driven-architecture/helm-chart/
helm upgrade -i --create-namespace -n default  mqtt .
# 5min

kubectl get pod,svc


kubectl port-forward --address 0.0.0.0 deployment/producer 5000:5000 &
kubectl port-forward --address 0.0.0.0 service/webserver 8080:80 &




### Monitoring stack
	helm repo add grafana https://grafana.github.io/helm-charts
	helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
	helm repo update
	kubectl create namespace monitoring
	helm -n monitoring install loki grafana/loki-stack --set loki.image.tag=2.9.1  
	helm -n monitoring install prometheus prometheus-community/prometheus
	helm -n monitoring install grafana grafana/grafana -f https://raw.githubusercontent.com/jpradoar/test/refs/heads/main/grafana-values.yaml

	kubectl -n monitoring port-forward --address 0.0.0.0 service/grafana 3000:80

















# Optional and usefull







### Identify Kubernetes Security, Reliability (polaris)
	helm repo add fairwinds-stable https://charts.fairwinds.com/stable
	helm upgrade -i polaris fairwinds-stable/polaris -n polaris --create-namespace
	kubectl port-forward --address 0.0.0.0 -n polaris svc/polaris-dashboard 8080:80


### Kubernetes API version deprecation (pluto)
	wget https://github.com/FairwindsOps/pluto/releases/download/v5.20.3/pluto_5.20.3_linux_amd64.tar.gz
	tar -xzvf pluto_5.20.3_linux_amd64.tar.gz
	sudo mv pluto /usr/local/bin/
	pluto detect-all-in-cluster
	pluto list-versions



### Chaos Engineering
	helm upgrade -i --create-namespace chaos-mesh chaos-mesh/chaos-mesh -n=chaos-mesh --version 2.7.0



	kind: ServiceAccount
	apiVersion: v1
	metadata:
	  namespace: default
	  name: account-default-viewer-user

	---
	kind: Role
	apiVersion: rbac.authorization.k8s.io/v1
	metadata:
	  namespace: default
	  name: role-default-viewer-user
	rules:
	- apiGroups: [""]
	  resources: ["pods", "namespaces"]
	  verbs: ["get", "watch", "list"]
	- apiGroups: ["chaos-mesh.org"]
	  resources: [ "*" ]
	  verbs: ["get", "list", "watch"]

	---
	apiVersion: rbac.authorization.k8s.io/v1
	kind: RoleBinding
	metadata:
	  name: bind-default-viewer-user
	  namespace: default
	subjects:
	- kind: ServiceAccount
	  name: account-default-viewer-user
	  namespace: default
	roleRef:
	  kind: Role
	  name: role-default-viewer-user
	  apiGroup: rbac.authorization.k8s.io


	kubectl -n default create token account-default-viewer-user

	kubectl -n default describe secrets account-default-viewer-user

	kubectl port-forward --address 0.0.0.0 -n chaos-mesh service/chaos-dashboard 2333:2333





### Helm charts deprecation version (nova)
	curl -L "https://github.com/FairwindsOps/nova/releases/download/3.2.0/nova_3.2.0_linux_amd64.tar.gz" > nova.tar.gz
	tar -xvf nova.tar.gz
	sudo mv nova /usr/local/bin/
	nova find -a --containers














### Otra documentación interesante:
	https://ofeng.org/posts/loki-grafana-prometheus-install-2024/
	https://github.com/kubernetes/kubernetes/issues/36152
	https://www.cncf.io/blog/2021/03/23/quick-application-deployments-on-microk8s-using-helm-charts/
	https://microk8s.io/#install-microk8s
	https://github.com/jpradoar/event-driven-architecture/tree/main/helm-chart