
start-gitlab-minikube:
	minikube start --driver=podman --container-runtime=cri-o
	minikube addons enable ingress

stop-gitlab-minikube:
	minikube stop

delete-minikube:
	minikube delete

start-gitlab-docker:
	export GITLAB_HOME=${PWD}/data && docker-compose up

register-runner-docker:
	docker run --rm -v ./data/runner:/etc/gitlab-runner --network gitlab_gitnet  gitlab/gitlab-runner register \
  --non-interactive \
  --executor "docker" \
  --docker-image alpine:latest \
  --url "http://web:80/" \
  --registration-token "X98MmhFPDFBifT-hB9Ly" \
  --description "docker-runner" \
  --maintenance-note "Free-form maintainer notes about this runner" \
  --tag-list "docker,aws" \
  --run-untagged="true" \
  --locked="false" \
  --access-level="not_protected"