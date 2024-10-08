# These can be overidden with env vars.
CLUSTER ?= nyu-devops

.SILENT:

.PHONY: help
help: ## Display this help.
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

.PHONY: all
all: help

##@ Development

.PHONY: clean
clean:	## Removes all dangling docker images
	$(info Removing all dangling docker images..)
	docker image prune -f

.PHONY: venv
venv: ## Create a Python virtual environment
	$(info Creating Python 3 virtual environment...)
	poetry config virtualenvs.in-project true
	poetry shell

.PHONY: install
install: ## Install dependencies
	$(info Installing dependencies...)
	sudo poetry config virtualenvs.create false
	sudo poetry install

.PHONY: lint
lint: ## Run the linter
	$(info Running linting...)
	flake8 service tests --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 service tests --count --max-complexity=10 --max-line-length=127 --statistics
	pylint service tests --max-line-length=127

.PHONY: tests
test: ## Run the unit tests
	$(info Running tests...)
	pytest --pspec --cov=service --cov-fail-under=95

##@ Runtime

.PHONY: run
run: ## Run the service
	$(info Starting service...)
	honcho start

.PHONY: cluster
cluster: ## Create a K3D Kubernetes cluster with load balancer and registry
	$(info Creating Kubernetes cluster with a registry and 1 node...)
	k3d cluster create --agents 1 --registry-create cluster-registry:0.0.0.0:5000 --port '8080:80@loadbalancer'

.PHONY: cluster-rm
cluster-rm: ## Remove a K3D Kubernetes cluster
	$(info Removing Kubernetes cluster...)
	k3d cluster delete

.PHONY: deploy
deploy: ## Deploy the service on local Kubernetes
	$(info Deploying service locally...)
	kubectl apply -f k8s/

.PHONY: knative
knative: ## Install Knative
	$(info Installing Knative in the Cluster...)
	kubectl apply -f https://github.com/knative/serving/releases/download/knative-v1.12.0/serving-crds.yaml
	kubectl apply -f https://github.com/knative/serving/releases/download/knative-v1.12.0/serving-core.yaml

.PHONY: tekton
tekton: ## Install Tekton
	$(info Installing Tekton in the Cluster...)
	kubectl apply --filename https://storage.googleapis.com/tekton-releases/pipeline/latest/release.yaml
	kubectl apply --filename https://storage.googleapis.com/tekton-releases/triggers/latest/release.yaml
	kubectl apply --filename https://storage.googleapis.com/tekton-releases/triggers/latest/interceptors.yaml
	kubectl apply --filename https://storage.googleapis.com/tekton-releases/dashboard/latest/tekton-dashboard-release.yaml

.PHONY: tekton-clean
tekton-clean: ## Clean up all PipelineRuns and TaskRuns
	$(info Cleaning up all PipelineRuns and TaskRuns...)
	tkn taskrun ls
	tkn taskrun rm --all -f
	tkn pipelinerun ls
	tkn pipelinerun rm --all -f

.PHONY: clustertasks
clustertasks: ## Create Tekton Cluster Tasks
	$(info Creating Tekton Cluster Tasks...)
	wget -qO - https://raw.githubusercontent.com/tektoncd/catalog/main/task/openshift-client/0.2/openshift-client.yaml | sed 's/kind: Task/kind: ClusterTask/g' | kubectl create -f -
	wget -qO - https://raw.githubusercontent.com/tektoncd/catalog/main/task/buildah/0.4/buildah.yaml | sed 's/kind: Task/kind: ClusterTask/g' | kubectl create -f -
