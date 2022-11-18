---
tags: [TP, Kubernetes]
aliases: ["CSV - TP3 sur Kubernetes", "TP3 sur Kubernetes - CSV"]
---

# TP3 - Cloud & Virtualisation - Kubernetes

> Eldar Kasmamytov, p1712650

## Déploiement du cluster
---

### Génération des clés ssh sur *Master*

```bash
ssh-keygen -N ""
```

## Utilisation du cluster
---

```bash
ubuntu@cvs-master-vm-eldar:~/rke$ kubectl get nodes
NAME              STATUS   ROLES               AGE     VERSION
192.168.246.106   Ready    controlplane,etcd   9m58s   v1.24.6
192.168.246.20    Ready    worker              9m40s   v1.24.6
192.168.246.76    Ready    worker              9m48s   v1.24.6
```

**Q:** Quel est l'état des nœuds ?  
**R:** L'état de tous les nœuds est `Ready`

### Création d'un Pod

```bash
ubuntu@cvs-master-vm-eldar:~/rke/objects$ kubectl get pods
NAME        READY   STATUS              RESTARTS   AGE
nginx-pod   0/1     ContainerCreating   0          13s
```

```bash
ubuntu@cvs-master-vm-eldar:~/rke/objects$ kubectl get pods -o wide
NAME        READY   STATUS    RESTARTS   AGE   IP          NODE             NOMINATED NODE   READINESS GATES
nginx-pod   1/1     Running   0          67s   10.42.1.5   192.168.246.76   <none>           <none>
```

**Q:** Sur quel nœud le Pod a-t-il été lancé ?  
**R:** Sur le nœud dont l'adresse IP est **192.168.246.76**, cela correspond au **Worker 1** dans mon cluster.

```bash
ubuntu@cvs-worker1-vm-eldar:~$ curl 192.168.246.76:8080
```

```html
<!DOCTYPE html>
<html>
<head>
<title>Welcome to nginx!</title>
<style>
html { color-scheme: light dark; }
body { width: 35em; margin: 0 auto;
font-family: Tahoma, Verdana, Arial, sans-serif; }
</style>
</head>
<body>
<h1>Welcome to nginx!</h1>
<p>If you see this page, the nginx web server is successfully installed and
working. Further configuration is required.</p>

<p>For online documentation and support please refer to
<a href="http://nginx.org/">nginx.org</a>.<br/>
Commercial support is available at
<a href="http://nginx.com/">nginx.com</a>.</p>

<p><em>Thank you for using nginx.</em></p>
</body>
</html>
```

Après avoir lancé une requête GET vers le Pod Nginx (port 8080) sur toutes les machines, on peut consulter les logs du Pod et vérifier que tout s'est bien passé:

```log
134.214.188.161 - - [14/Nov/2022:10:16:03 +0000] "GET / HTTP/1.1" 200 615 "-" "curl/7.81.0" "192.168.246.76"
134.214.188.161 - - [14/Nov/2022:10:17:06 +0000] "GET / HTTP/1.1" 200 615 "-" "curl/7.81.0" "192.168.246.20"
134.214.188.161 - - [14/Nov/2022:10:17:14 +0000] "GET / HTTP/1.1" 200 615 "-" "curl/7.81.0" "192.168.246.106"
```

**Q:** Que pouvez-vous conclure ?  
**R:** En intérrogeant le Pod Nginx sur le port 8080, on obtient bien une réponse, la page HTML par défaut de Nginx. Ainsi, le Pod Nginx créé est bien fonctionnel.

### Création d'un Deployment

```bash
ubuntu@cvs-master-vm-eldar:~/rke/objects$ kubectl get deployments -o wide
NAME               READY   UP-TO-DATE   AVAILABLE   AGE     CONTAINERS   IMAGES   SELECTOR
nginx-deployment   3/3     3            3           3m27s   nginx        nginx    app=web
```

**Q:** Quels rôles jouent les labels et les sélecteurs ?  
**R:** Les *labels* sont des propriétés complémentaires qui n'impactent pas la déscription interne des objets et qui sont utiles aux utilisateurs. Les *selectors* peuvent être utilisés pour filtrer des objets par leur *labels*, par exemple pour conditionner la sélection de nœud dans la déscription des *Pods*.

**Q:** Sur quelle image seront basés les conteneurs créés ?  
**R:** Sur l'image `nginx`

**Q:** Combien de replicas ont été créés par le déploiement ?  
**R:** Pour `nginx`, 3 replicas ont été créés.

**Q:** Que voyez-vous dans la liste des événements de déploiement ?  
**R:** On remarque 2 événements, ils correspondent aux 2 mises à l'échelle du déploiement, 3 replicas et 6 replicas réspectivement.

```bash
Type    Reason             Age   From                   Message
----    ------             ----  ----                   -------
Normal  ScalingReplicaSet  10m   deployment-controller  Scaled up replica set nginx-deployment-cff6559d7 to 3
Normal  ScalingReplicaSet  28s   deployment-controller  Scaled up replica set nginx-deployment-cff6559d7 to 6
```

**Q:** Comment sont distribués les pods entre les nœuds Workers ?  
**R:** Après avoir executé la commande `kubectl get pods -o wide` pour afficher tous les pods, on constate qu'ils sont distribués à égalité. Les 3 premiers pods créés sont partagés entre les deux workers comme suit 2/1 et les 3 restants comme suit 1/2. Ainsi, chaque worker gère 3 pods.

**Q:** Quel est l'intérêt de la section `selector` dans le fichier yaml ?  
**R:** Les *selectors* dans un *Deployment* sont utiles à gérer ses *Pods*. En effet, un *Deployment* filtre les *Pods* en fonction de leur libellés, donc les 2 libellés `.spec.selector` et `.spec.template.metadata.labels` doivent être les mêmes dans la déscription de ce *Deployment*. C'est utile par exemple pour maintenir un nombre de `replicas`.

### Création d'un Service

**Q:** Que permet de faire un **Service** de type `NodePort` ?  
**R:** Ce service permet de "bind" les ports internes/externes.

**Q:** Détecter quel **port** est exposé sur les nœuds pour atteindre le service  
**R:** La commande `kubectl get services -o wide` montre que les ports exposés sont `80:31857/TCP`

**Q:** Quelles adresses sont affichées dans la liste des ENDPOINTS ?  
**R:** La commande `kubectl get endpoints -o wide` affiche:  
  - 10.42.1.6:80
  - 10.42.1.7:80
  - 10.42.1.8:80
  - \+ 3 more...

Le déploiement est bien accéssible depuis chaque nœud du cluster (via `curl -I 127.0.0.1:31857`)
```http
HTTP/1.1 200 OK
Server: nginx/1.23.2
Date: Mon, 14 Nov 2022 11:27:21 GMT
Content-Type: text/html
Content-Length: 615
Last-Modified: Wed, 19 Oct 2022 07:56:21 GMT
Connection: keep-alive
ETag: "634fada5-267"
Accept-Ranges: bytes
```

Il est également disponible depuis le pod `nginx-pod` créé précédemment:
```bash
ubuntu@cvs-master-vm-eldar:~/rke/objects$ kubectl exec nginx-pod -- curl http://nginx-service
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   615  100   615    0     0   150k      0 --:--:-- --:--:-- --:--:--  150k
```

### Rolling Updates

```bash
kubectl rollout history deployment nginx-deployment
```

```log
deployment.apps/nginx-deployment
REVISION  CHANGE-CAUSE
2         <none>
3         <none>
```

**Q:** Affichez les détails de la révision 2 du Deployment. Quelle commande utiliserez-vous ?  
**R:** Après avoir consulté la page d'aide pour la commande `history` (avec l'option `-h`), on s'aperçoit qu'il existe une option pour afficher les détails d'une révision. Ainsi, afin d'afficher les détails de la révision **2**:

```bash
kubectl rollout history --revision=2 deployment nginx-deployment
```

```log
deployment.apps/nginx-deployment with revision #2
Pod Template:
  Labels:       app=web
        pod-template-hash=565998cb8f
  Containers:
   nginx:
    Image:      nginx:1.16.0
    Port:       80/TCP
    Host Port:  0/TCP
    Environment:        <none>
    Mounts:     <none>
  Volumes:      <none>
```

**Q:** Revenez à la révision 2 du déploiement. Quelle commande avez-vous utilisé ?  
**R:** La commande suivante `kubectl rollout undo --to-revision=2 deployments nginx-deployment`

### Volumes

#### Création d'un Persistent Volume

**Q:** Que signifie l'accès mode "ReadWriteOnce"?  
**R:** Il signifie que ce volume peut être monté par un seul nœud à la fois en mode "ReadWrite". Cependant, plusieurs *Pods* **dans le même nœud** peuvent quand même accéder ce volume en même temps.

**Q:** Quel est le statut du PV après création ?  
**R:** Le statut est `Available`, donc prêt à "claim".

**Q:** Quelle est la stratégie de rétention de volume persistant créée et que signifie-t-elle ?  
**R:** La commande `kubectl get pv` montre que RECLAIM POLICY est `Retain`. Cela veut dire lorsque le Persistent Volume Claim (PVC) associé est supprimé, le Persistent Volume lui-même sera gardé. Cela permet "reclaim" manuel du volume.

#### Création d'un Persistent Volume Claim

**Q:** Quel est le statut du PV et du PVC après la création de la claim ?  
**R:** Les deux PV et PVC ont le même statut `Bound`. Le *Control Plane* a automatiquement assigné le PV créé précédemment au PVC.

**Q:** Est-ce que deux claims peuvent utiliser le même volume persistant ?  
**R:** D'après [la documentation en ligne de **K8s**](https://kubernetes.io/docs/concepts/storage/persistent-volumes/#binding), les "bindings" à partir des PVC vers les PV sont des "mappings one-to-one". En principe, il ne doit pas être possible d'utiliser le même PV.  

Après avoir créé et appliqué un autre PVC, on voit qu'effectivement il n'est pas possible d'utiliser le même PV, puisque le statut du nouveau PVC est `Pending`.

**Q:** Trouvez un moyen de vérifier que le volume persistent fonctionne correctement. Comment l'avez-vous vérifié ?  
**R:** Le stockage est alloué est sur un des nœuds *Worker* dans le chemin spécifié lors de la création du PV (`/mnt/data`). En listant le répértoire sur les nœuds *Worker* (avec `ls -la /mnt/data`), on voit qu'il est bien présent sur le nœud *Worker 1* et contient des fichiers, notamment les fichiers du container `mongodb` créé.

### Variables d'environnement

**Q:** Que voyez-vous dans les logs du Pod?  
**R:** `Username: administrator`

### Secrets

**Q:** Quel est le contenu du fichier `secret.yml` après les modifications ?  
**R:** La chaîne "Lyon1" encodée en *base64* avec `echo -n "Lyon1" | base64` est "`THlvbjE=`". Ainsi, le contenu du fichier `secret.yml` est:

```yml
apiVersion: v1
kind: Secret
metadata:
  name: 42-secret
data:
  username: THlvbjE=
  password: THlvbjE=
```

**Q:** Quelle sera la nouvelle description du Pod avec des secrets ?  
**R:** Le nouveau contenu du fichier de description est:

```yml
apiVersion: v1
kind: Pod
metadata:
  name: pod-with-secret
spec:
   containers:
   - name: busybox
     image: busybox
     command: ['sh', '-c', 'ls -al /secret && echo "Username: $SECRET_USERNAME" && sleep 99999']
     env:
     - name: SECRET_USERNAME
       valueFrom:
         secretKeyRef:
           name: 42-secret
           key: username
     volumeMounts:
     # name must match the volume name below
     - name: secret-volume
       mountPath: /secret
   # The secret data is exposed to Containers in the Pod through a Volume.
   volumes:
   - name: secret-volume
     secret:
       secretName: 42-secret
```

**Q:** Que voyez-vous dans les logs du Pod ?  
**R:** L'affichage produit est:

```log
total 4
drwxrwxrwt    3 root     root           120 Nov 17 18:22 .
drwxr-xr-x    1 root     root          4096 Nov 17 18:22 ..
drwxr-xr-x    2 root     root            80 Nov 17 18:22 ..2022_11_17_18_22_14.2696919416
lrwxrwxrwx    1 root     root            32 Nov 17 18:22 ..data -> ..2022_11_17_18_22_14.2696919416
lrwxrwxrwx    1 root     root            15 Nov 17 18:22 password -> ..data/password
lrwxrwxrwx    1 root     root            15 Nov 17 18:22 username -> ..data/username
Username: Lyon1
```

### Init containers

**Q:** Sur quel nœud Worker le Pod a-t-il été lancé ?  
**R:** Après avoir lancé `kubectl get pods -o wide`, on voit que le Pod a été démarré sur le nœud dont l'adresse IP est **192.168.246.20**, cela correspond au **Worker 2** dans mon cluster.

**Q:** Que vous renvoie la commande `curl` ?  
**R:** "Kubernetes"

### Sondes de Liveness et Readiness

Kubernetes propose trois mécanismes: sondes de **Liveness**, **Readiness** et **Startup**.

#### Liveness probe

**Q:** Que fait Kubernetes en cas d'échec de la Liveness probe ?  
**R:** Le Pod a été automatiquement relancé par K8s, on peut le voir dans l'attribut RESTARTS (qui est devenu 1) affiché par la commande `kubectl get pods -o wide`.

#### Readiness probe

**Q:** Que remarquez-vous ?  
**R:** Un des pods créés (`nginx-nogood`) a échoué à se lancer, son statut est `ErrImagePull`, ce qui est normal, puisque il n'existe pas d'image `nginx:1.222`.

**Q:** La liste des endpoints du service. Que remarquez-vous ?  
**R:** L'endpoint `nginx-readiness` a été créé avec l'adresse IP suivante `10.42.2.18:80`, ce qui correspond au Pod `nginx-good`.

**Q:** Est-ce que le service répond aux requêtes ? Comment pouvez-vous expliquer un tel comportement ?  
**R:** Oui, le service répond aux requêtes. Même si `nginx-nogood` n'est pas opérationnel, on a toujours un autre Pod fonctionnel exposé sur ce NodePort (`nginx-good`), c'est donc lui qui répond aux requêtes.

**Q:** Trouvez et corrigez l'erreur. Que remarquez-vous ?  
**R:** Après avoir corrigé la version du Pod, il a réussi à se démarrer. De plus, la commande `kubectl get endpoints` montre que ce Pod a été rajouté dans le service `nginx-readiness` (son adresse IP `10.42.1.20:80` est apparue dans l'attribut ENDPOINTS).

### Création d'un Ingress

**Q:** Quelles adresses se trouvent dans la colonne ADDRESS ?  
**R:** C'est les adresses IP de mes nœuds *Worker* (`192.168.246.20,192.168.246.76`). 

**Q:** Essayez d'accéder au **Service** en utilisant le nom DNS précédemment créé à parir de votre navigateur ou en executant la commande `curl`. Que pouvez-vous constater ?  
**R:** `ping kasmamytov.cloudtiw.os.univ-lyon1.fr` reçoit bien des *pongs*. De plus, on peut vérifier que les deux nœuds sont enrégistrées avec ce nom de domaine via `host -a kasmamytov.cloudtiw.os.univ-lyon1.fr`.

## Un déploiement plus complexe

### Service Redis

#### Persistent Volume

```yml
kind: PersistentVolume
apiVersion: v1
metadata:
  name: redis-pv
spec:
  capacity:
    storage: 500Mi
  accessModes:
    - ReadWriteOnce
  hostPath:
    path: "/mnt/redis"
```

#### Persistent Volume Claim (redis-data)

```yml
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: redis-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 500Mi
```

#### Secret

##### Encoder le mot de passe en *base64*

```bash
$ echo -n "redispassword" | base64
cmVkaXNwYXNzd29yZA==
```

##### Description de l'objet

```yml
kind: Secret
apiVersion: v1
metadata:
  name: redis-secret
data:
  password: cmVkaXNwYXNzd29yZA==
```

#### Deployment

```yml
kind: Deployment
apiVersion: apps/v1
metadata:
  name: redis-deployment
spec:
  selector:
    matchLabels:
      app: redis
  replicas: 1
  template:
    metadata:
      labels:
        app: redis
    spec:
      volumes:
      - name: redis-config
        emptyDir: {}
      - name: redis-data
        persistentVolumeClaim:
          claimName: redis-pvc
      containers:
      - name: redis
        image: redis
        command: ["redis-server", "/etc/redis/redis.conf"]
        volumeMounts:  
        - mountPath: /etc/redis/  
          name: redis-config
        - mountPath: /data
          name: redis-data
        livenessProbe:
          exec:
            command: ["redis-cli", "ping"]
      initContainers:
      - name: redis-config-init
        image: busybox
        command: ["sh", "-c", "echo requirepass $PASSWORD > /etc/redis/redis.conf"]
        volumeMounts:  
        - mountPath: /etc/redis/
          name: redis-config
        env:
        - name: PASSWORD
          valueFrom:
            secretKeyRef:
              name: redis-secret
              key: password
```

#### Service

```yml
kind: Service
apiVersion: v1
metadata:
  name: redis-service
spec:
  type: ClusterIP
  selector:
    app: redis
  ports:
  - protocol: TCP
    port: 6379
    targetPort: 6379
```

### Service Counter

#### Deployment

```yml
kind: Deployment
apiVersion: apps/v1
metadata:
  name: counter-deployment
spec:
  selector:
    matchLabels:
      app: counter
  replicas: 1
  template:
    metadata:
      labels:
        app: counter
    spec:
      volumes:
      - name: counter-app
        emptyDir: {}
      - name: redis-secret
        secret:
          secretName: redis-secret
      containers:
      - name: counter-app
        image: vladost/php:7.2-apache-redis
        env:
        - name: REDIS_HOST
          value: redis-service
        volumeMounts:
        - mountPath: /var/www/html
          name: counter-app
        - mountPath: /credentials
          name: redis-secret
        livenessProbe:
          httpGet:
            path: /
            port: 80
      initContainers:
      - name: counter-app-init
        image: busybox
        command: ['wget', 'https://forge.univ-lyon1.fr/vladimir.ostapenco/counter-application/-/raw/main/index.php', '-O', '/var/www/html/index.php']
        volumeMounts:  
        - mountPath: /var/www/html
          name: counter-app
```

#### Service

```yml
kind: Service
apiVersion: v1
metadata:
  name: counter-service
spec:
  selector:
    app: counter
  ports:
  - protocol: TCP
    port: 80
    targetPort: 80
```

#### Ingress

```yml
kind: Ingress
apiVersion: networking.k8s.io/v1
metadata:
  name: counter-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - http:
      paths:
      - path: /counter
        pathType: Prefix
        backend:
          service:
            name: counter-service
            port:
              number: 80
```

### Verification de l'application

En passant par [mon URL de déploiement](http://kasmamytov.cloudtiw.os.univ-lyon1.fr/counter) dans le navigateur, j'obtiens le résultat suivant:

```
Starting application...  
Counter service was successfully started...  
----------------------------------------------  
Service usage counter: **82**  
Current service instance: **counter-deployment-7bb696c996-jjx76**  
----------------------------------------------
```

- En ce moment, le compteur vaut 82.
- Le nom de l'instance de service correspond bien au celui dans mon cluster (peut-être vérifié avec la commande `kubectl get pods -o wide`).

**Q:** Surveillez la valeur du compteur, attendez une minute et mettez à jour la page. Que remarquez-vous ? Comment pouvez-vous l'expliquer ?  
**R:** La valeur du compteur s'incrémente lors de chaque visite de la page. Mais cela ne s'applique qu'aux visites de l'utilisateur. Le fait que le compteur s'incrémente tout seul due aux sondes de liveness, qui sont faites chaque 10 secondes (comportement par défaut selon [la doc officielle](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/#configure-probes)). De ce fait, au bout d'une minute, le compteur augmentera de 6.

