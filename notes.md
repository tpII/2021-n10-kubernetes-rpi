*Preparativos*

Enabling cgroups for Raspbian Busterhttps://rancher.com/docs/k3s/latest/en/installation/installation-requirements/

Enabling cgroups for Raspbian Buster & Enabling legacy iptables on Raspbian Buster: https://rancher.com/docs/k3s/latest/en/advanced/

K3s necesita tener activado algo llamado *cgroup* para poder ejecutar los contenedores. Raspbian buster tiene dicha caracteristica desactivada por defecto. Para habilitarla:

modificar el archivo /boot/cmdline.txt

    sudo nano /boot/cmdline.txt

agregar al final

    cgroup_memory=1 cgroup_enable=memory

Para operar, todo debe realizarse siendo root desde este punto

    sudo su -

K3s necesita ademas utilizar algo llamado Legacy IP Tables. Raspbian buster utiliza por defecto nftables, por lo que debemos configurarlo para utilizar legacy iptables

    sudo iptables -F
    sudo update-alternatives --set iptables /usr/sbin/iptables-legacy
    sudo update-alternatives --set ip6tables /usr/sbin/ip6tables-legacy

reiniciamos el sistema

    sudo reboot

*Instalación en el nodo maestro*

Una vez realizados los preparativos, instalamos K3s en modo superusuario

Tener en cuenta que K3s usa por default a containerd como el Container Runtime. A fin de simplificar la guia, pasaremos a utilizar containerd.

el siguiente comando se encarga de descargar un script provisto por Rancher (los creadores de K3s), el cual se encargará de realizar la instalación

A su vez, rancher recomienda una herramienta Rancher, que facilita el manejo de distintas plataformas de Kubernetes. Aunque no es necesaria para nuestro caso, dejaremos la instalación de K3s lista en caso de que decidamos probarla, ya que según rancher, no causará problemas en caso de dejarse activada.



https://rancher.com/docs/k3s/latest/en/quick-start/
https://rancher.com/docs/rancher/v2.5/en/cluster-provisioning/registered-clusters/

    sudo su -

    curl -sfL https://get.k3s.io | sh -s - --write-kubeconfig-mode 644

Una vez finalizada la instalación, debido a que la capacidad de las SBC es bastante limitada y que un orquestador de Kubernetes es algo pesado, es recomendable volver a reiniciar el sistema para finalizar cualquier proceso que no sea necesario.

A diferencia de antes,esperar algunos minutos hasta que la actividad del cpu baje antes de operar sobre el sistema. (se recomienda utilizar htop para monitorear la actividad)

Luego de unos minutos, comprobamos el estado del sistema utilizando haciendo que liste los nodos que tiene conectados. En este caso, solo se listará a si mismo, ya que no hay otros nodos.

    sudo su -

    kubectl get nodes

*Instalacion en nodos worker*

Es necesario realizar los mismos preparativos que para el nodo maestro, pero la instalación cambia un poco.

Para instalar K3s en un nodo trabajador, debemos tener la direccion ip y el token de autenticación del nodo maestro.

La dirección ip ya la conocemos por haberla seteado antes. de todas formas, si no se la conoce, puede encontrarse utilizando el comando

    ipfconfig -a | grep -A 7 "eht0"

Utilizamos eth0 porque es la interfaz que configuramos inicialmente

El Token de autenticación puede encontrarse en el archivo /var/lib/rancher/k3s/server/node-token, por lo que simplemente hacemos un cat para verlo y copiarlo.

    cat /var/lib/rancher/k3s/server/node-token

Teniendo la dirección ip y el token, iniciamos una sesion mediante ssh con uno de los nodos trabajadores. En la instalación, seteamos dichos parametros mediante las variables de entorno K3S_URL y K3S_TOKEN
Es importante mensionar que para que K3s funcione, cada nodo debe tener un hostname diferente. En nuestro caso, todos los nodos tienen por nombre 'raspberry', por lo que para cambiarlo, editamos tambien la variable de ambiente correspondiente al nobmre del nodo, K3S_NODE_NAME.

    sudo su -

    curl -sfL https://get.k3s.io | K3S_URL=https://[ip_del_nodo_maestro]:6443 K3S_TOKEN=[token_del_nodo_maestro] K3S_NODE_NAME="[nombre_del_nuevo_nodo]" sh -

En nuestro caso, utilizamos la configuración:

    sudo su

    curl -sfL https://get.k3s.io | K3S_URL=https://192.168.0.201:6443 K3S_TOKEN=K1001dec79df9dfa648fe3633367dc8cdfd182bb7260444e40ebafa9fbcf5950320::server:a2aa8e621c89ee0bbd309b3d11c191d0 K3S_NODE_NAME="worker1" sh -


