# TableDiffGenerator unter Kubernetes

Diese Anleitung beschreibt einen einfachen Einstieg, um die Webversion von
TableDiffGenerator in Kubernetes laufen zu lassen. Der Fokus liegt auf Rancher
Desktop als lokale Spielumgebung. Rancher Server wird danach ähnlich genutzt,
benötigt aber normalerweise eine erreichbare Container Registry.

## Zielbild

Die Anwendung besteht im Kubernetes-Cluster aus:

- einem Docker-Image mit der Flask/Gunicorn-Webanwendung
- einem Helm Chart unter `Kubernetes/helm/tablediffgenerator`
- einem `Deployment` für den Pod
- einem `Service` für den Zugriff innerhalb des Clusters
- optional einem `Ingress` für Zugriff über Hostname

Für den ersten Test ist **kein Ingress nötig**. Am einfachsten ist:

```bash
kubectl port-forward
```

## Voraussetzungen

Installiert und gestartet:

- Rancher Desktop mit aktiviertem Kubernetes
- `kubectl`
- `helm`
- Docker-kompatibles Build-Werkzeug

Prüfen:

```bash
kubectl version --client
kubectl cluster-info
helm version
```

Wenn `kubectl cluster-info` keinen Cluster findet, ist Kubernetes in Rancher
Desktop vermutlich noch nicht aktiviert oder der falsche Kubernetes-Kontext
ausgewählt.

Kontext anzeigen:

```bash
kubectl config current-context
kubectl config get-contexts
```

## 1. Image lokal bauen

Im Projektwurzelverzeichnis:

```bash
docker build -f Docker/Dockerfile -t tablediffgenerator-web:local .
```

Falls Rancher Desktop mit `containerd` statt `dockerd/moby` arbeitet, kann der
Build stattdessen so nötig sein:

```bash
nerdctl -n k8s.io build -f Docker/Dockerfile -t tablediffgenerator-web:local .
```

Wichtig ist, dass das Image im Runtime-Speicher des lokalen Kubernetes-Clusters
landet. Das Chart nutzt standardmäßig:

```text
tablediffgenerator-web:local
```

und `imagePullPolicy: IfNotPresent`.

## 2. Namespace anlegen

```bash
kubectl create namespace tablediff
```

Falls der Namespace schon existiert, ist die Fehlermeldung unkritisch.

## 3. Helm Chart installieren

```bash
helm upgrade --install tablediffgenerator Kubernetes/helm/tablediffgenerator \
  --namespace tablediff
```

Status prüfen:

```bash
kubectl -n tablediff get pods
kubectl -n tablediff get service
```

Der Pod sollte nach kurzer Zeit `Running` anzeigen.

Details bei Problemen:

```bash
kubectl -n tablediff describe pod -l app.kubernetes.io/name=tablediffgenerator
kubectl -n tablediff logs -l app.kubernetes.io/name=tablediffgenerator
```

## 4. Anwendung öffnen

Für den ersten Test:

```bash
kubectl -n tablediff port-forward service/tablediffgenerator 8080:80
```

Danach im Browser öffnen:

```text
http://127.0.0.1:8080
```

Der Health-Check der Anwendung ist hier erreichbar:

```text
http://127.0.0.1:8080/healthz
```

## 5. Aktualisieren nach Codeänderungen

Image neu bauen:

```bash
docker build -f Docker/Dockerfile -t tablediffgenerator-web:local .
```

Deployment neu starten:

```bash
kubectl -n tablediff rollout restart deployment/tablediffgenerator
kubectl -n tablediff rollout status deployment/tablediffgenerator
```

Bei `containerd` entsprechend wieder mit `nerdctl -n k8s.io build ...` bauen.

## 6. Deinstallieren

```bash
helm uninstall tablediffgenerator --namespace tablediff
kubectl delete namespace tablediff
```

## Option: Ingress aktivieren

Ingress ist für den ersten Test nicht nötig. Wenn Rancher Desktop einen
Ingress Controller bereitstellt, kann der Zugriff per Hostname aktiviert werden:

```bash
helm upgrade --install tablediffgenerator Kubernetes/helm/tablediffgenerator \
  --namespace tablediff \
  --set ingress.enabled=true \
  --set 'ingress.hosts[0].host=tablediffgenerator.localhost'
```

Danach:

```text
http://tablediffgenerator.localhost
```

Falls das nicht funktioniert, zuerst prüfen, ob ein Ingress Controller läuft:

```bash
kubectl get ingressclass
kubectl -n ingress-nginx get pods
```

Je nach Rancher-Desktop-Setup kann der Namespace oder die Ingress-Klasse anders
heißen. Für Anfänger ist Port-Forward daher der zuverlässigere erste Weg.

## Rancher Server

Bei einem Rancher-Server-Cluster läuft Kubernetes meistens nicht auf dem lokalen
Rechner. Dann reicht ein lokal gebautes Image nicht aus. Das Image muss in eine
Registry gepusht werden, die der Cluster erreichen kann.

Beispiel:

```bash
docker build -f Docker/Dockerfile -t registry.example.com/tablediffgenerator-web:0.3.0 .
docker push registry.example.com/tablediffgenerator-web:0.3.0
```

Installation mit diesem Image:

```bash
helm upgrade --install tablediffgenerator Kubernetes/helm/tablediffgenerator \
  --namespace tablediff \
  --create-namespace \
  --set image.repository=registry.example.com/tablediffgenerator-web \
  --set image.tag=0.3.0
```

Wenn die Registry privat ist, wird zusätzlich ein `imagePullSecret` benötigt.
Das Chart ist dafür vorbereitet:

```bash
kubectl -n tablediff create secret docker-registry registry-credentials \
  --docker-server=registry.example.com \
  --docker-username=<benutzer> \
  --docker-password=<passwort>

helm upgrade --install tablediffgenerator Kubernetes/helm/tablediffgenerator \
  --namespace tablediff \
  --set image.repository=registry.example.com/tablediffgenerator-web \
  --set image.tag=0.3.0 \
  --set 'imagePullSecrets[0].name=registry-credentials'
```

## Wichtige Chart-Werte

Die wichtigsten Einstellungen stehen in:

```text
Kubernetes/helm/tablediffgenerator/values.yaml
```

Häufige Werte:

- `image.repository`: Name der Container-Image-Repository
- `image.tag`: Image-Version
- `service.type`: meistens `ClusterIP`
- `container.maxUploadSize`: maximale Uploadgröße in Bytes
- `ingress.enabled`: Ingress ein- oder ausschalten
- `resources`: CPU- und Speichergrenzen

Werte können beim Installieren überschrieben werden:

```bash
helm upgrade --install tablediffgenerator Kubernetes/helm/tablediffgenerator \
  --namespace tablediff \
  --set container.maxUploadSize=67108864
```
