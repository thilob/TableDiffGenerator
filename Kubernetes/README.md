# TableDiffGenerator unter Kubernetes

Diese Anleitung beschreibt einen einfachen Einstieg, um die Webversion von
TableDiffGenerator in Kubernetes laufen zu lassen. Der Fokus liegt auf Rancher
Desktop als lokale Spielumgebung. Rancher Server wird danach ähnlich genutzt,
benötigt aber normalerweise eine erreichbare Container Registry.

## Zielbild

Die Anwendung besteht im Kubernetes-Cluster aus:

- einem Docker-Image mit der Flask/Gunicorn-Webanwendung
- optional einem veröffentlichten Image aus GitHub Packages / GHCR
- einem Helm Chart unter `Kubernetes/helm/tablediffgenerator`
- einem `Deployment` für den Pod
- einem `Service` für den Zugriff innerhalb des Clusters
- einem `Ingress` für Zugriff über Hostname in Rancher Desktop

Der Lernpfad ist:

```text
Port-Forward -> NodePort -> Ingress
```

Im Chart ist die Ingress-Variante aus Sicherheitsgründen standardmäßig
deaktiviert. NodePort ist als kommentierte Variante in `values.yaml` erhalten.

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

## 1a. Image aus GitHub Packages nutzen

Alternativ zum lokalen Build kann Kubernetes das veröffentlichte Container-Image
aus GitHub Packages ziehen:

```text
ghcr.io/thilob/tablediffgenerator-web:kubernetes-latest
```

Dafür ist eine eigene Values-Datei vorbereitet:

```bash
helm upgrade --install tablediffgenerator Kubernetes/helm/tablediffgenerator \
  --namespace tablediff \
  --create-namespace \
  -f Kubernetes/helm/tablediffgenerator/values-ghcr.yaml
```

Das ist vor allem für Rancher Server oder andere Cluster sinnvoll, die nicht auf
deinen lokalen Docker-Image-Speicher zugreifen können.

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

Die Standardinstallation veröffentlicht die Anwendung nicht nach außen. Für den
ersten Test eignet sich ein direkter Service-Port-Forward:

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

### Optional: Zugriff per Traefik Ingress

Für Rancher Desktop kann der Ingress bewusst aktiviert werden:

```bash
helm upgrade --install tablediffgenerator Kubernetes/helm/tablediffgenerator \
  --namespace tablediff \
  --set ingress.enabled=true
```

Danach nutzt die Installation Traefik Ingress:

```text
http://tablediffgenerator.localhost
```

Health-Check:

```text
http://tablediffgenerator.localhost/healthz
```

Prüfen:

```bash
kubectl -n tablediff get ingress
kubectl get ingressclass
```

Wenn Rancher Desktop Traefik nicht direkt auf Port 80 des lokalen Rechners
veröffentlicht, kann der Ingress trotzdem über einen Port-Forward auf Traefik
getestet werden:

```bash
kubectl -n kube-system port-forward service/traefik 18081:80
```

Danach im Browser öffnen:

```text
http://tablediffgenerator.localhost:18081
```

Dieser Weg nutzt weiterhin die Ingress-Regel mit dem Hostnamen
`tablediffgenerator.localhost`; nur der Traefik-Einstieg wird lokal
durchgereicht.

### Optional: Basic-Auth per Secret

Für öffentlich erreichbare Installationen sollte die Webversion mit
Authentifizierung und TLS betrieben werden. Ein Secret für Basic-Auth kann so
angelegt werden:

```bash
kubectl -n tablediff create secret generic tablediff-basic-auth \
  --from-literal=username=tablediff \
  --from-literal=password='ein-langes-passwort'
```

Danach Auth im Chart aktivieren:

```bash
helm upgrade --install tablediffgenerator Kubernetes/helm/tablediffgenerator \
  --namespace tablediff \
  --set auth.enabled=true \
  --set auth.existingSecret=tablediff-basic-auth
```

Der Health-Check `/healthz` bleibt ohne Authentifizierung erreichbar.

## 5. Nachverfolgbar: Zugriff per NodePort

NodePort ist ein guter Zwischenschritt vor Ingress. Der Service bekommt dabei
einen festen Port auf dem Kubernetes-Node. Diese Variante ist im Chart nicht
aktiv, aber in `values.yaml` kommentiert dokumentiert.

```bash
helm upgrade --install tablediffgenerator Kubernetes/helm/tablediffgenerator \
  --namespace tablediff \
  --set service.type=NodePort \
  --set service.nodePort=30080 \
  --set ingress.enabled=false
```

Service prüfen:

```bash
kubectl -n tablediff get service tablediffgenerator
```

Danach ist die Anwendung in Rancher Desktop typischerweise hier erreichbar:

```text
http://127.0.0.1:30080
```

Health-Check:

```text
http://127.0.0.1:30080/healthz
```

Zurück zum internen ClusterIP-Service:

```bash
helm upgrade --install tablediffgenerator Kubernetes/helm/tablediffgenerator \
  --namespace tablediff \
  --set service.type=ClusterIP \
  --set service.nodePort=null \
  --set ingress.enabled=false
```

Wenn Rancher die Replikazahl über die Oberfläche verändert hat, kann Helm 4
beim Upgrade einen Field-Manager-Konflikt melden, z. B. für `.spec.replicas`.
Dann entweder die gewünschte Replikazahl explizit mitgeben oder erst in Rancher
zurückstellen. Beispiel, wenn aktuell 5 Replikas gewünscht sind:

```bash
helm upgrade --install tablediffgenerator Kubernetes/helm/tablediffgenerator \
  --namespace tablediff \
  --set service.type=NodePort \
  --set service.nodePort=30080 \
  --set ingress.enabled=false \
  --set replicaCount=5 \
  --force-conflicts
```

## 6. Aktualisieren nach Codeänderungen

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

## 7. Deinstallieren

```bash
helm uninstall tablediffgenerator --namespace tablediff
kubectl delete namespace tablediff
```

## Ingress

Ingress ist die aktive Standardvariante des Charts. Rancher Desktop bringt bei
aktivierter Traefik-Option bereits einen passenden Ingress Controller mit.

```bash
helm upgrade --install tablediffgenerator Kubernetes/helm/tablediffgenerator \
  --namespace tablediff
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

Für dieses Projekt ist GitHub Packages / GHCR als Standard-Registry vorbereitet:

```bash
helm upgrade --install tablediffgenerator Kubernetes/helm/tablediffgenerator \
  --namespace tablediff \
  --create-namespace \
  -f Kubernetes/helm/tablediffgenerator/values-ghcr.yaml
```

Das Chart nutzt dann:

```text
ghcr.io/thilob/tablediffgenerator-web:kubernetes-latest
```

Ein Beispiel mit einer eigenen Registry:

```bash
docker build -f Docker/Dockerfile -t registry.example.com/tablediffgenerator-web:0.4.1 .
docker push registry.example.com/tablediffgenerator-web:0.4.1
```

Installation mit diesem Image:

```bash
helm upgrade --install tablediffgenerator Kubernetes/helm/tablediffgenerator \
  --namespace tablediff \
  --create-namespace \
  --set image.repository=registry.example.com/tablediffgenerator-web \
  --set image.tag=0.4.1
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
  --set image.tag=0.4.1 \
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
- `service.type`: standardmäßig `ClusterIP`; `NodePort` ist als kommentierte Variante dokumentiert
- `service.nodePort`: fester NodePort, z. B. `30080`, wenn NodePort explizit aktiviert wird
- `container.maxUploadSize`: maximale Uploadgröße in Bytes
- `ingress.enabled`: Ingress ein- oder ausschalten
- `resources`: CPU- und Speichergrenzen

Werte können beim Installieren überschrieben werden:

```bash
helm upgrade --install tablediffgenerator Kubernetes/helm/tablediffgenerator \
  --namespace tablediff \
  --set container.maxUploadSize=67108864
```
