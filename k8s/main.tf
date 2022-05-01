provider "helm" {
  kubernetes {
    config_path = "~/.kube/config"
  }
}

resource "helm_release" "gitlab" {
  name = "gitlab"

  repository = "https://charts.gitlab.io/"
  chart      = "gitlab"
  namespace  = "default"
  values = [
    file("values-minikube.yaml")
  ]
  timeout = "6000"

  set {
    name  = "timeout"
    value = "6000s"
  }

  set {
    name = "gitlab.migrations.initialRootPassword.key"
    value ="foobarTestPassword!"
  }
}