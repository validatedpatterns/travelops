# TravelOps Test Plan

[GitHub Repository](https://github.com/validatedpatterns/travelops)

## PreRequisites

- Running OpenShift Cluster (3Node, 3x(n)) - Can be HyperShift or traditional OpenShift cluster
- Logged into cluster or exported KUBECONFIG

## Deployment

1. Copy the secrets template file to your home directory:

```shell
cp values-secret.yaml.template $HOME/values-secret-travelops.yaml
```

1. Run pattern.sh wrapper script

```shell
./pattern.sh make install
```

1. Get the route to the travel control portal

```shell
CONTROL=http://$(oc get gtw travel-control-gateway -n travel-control -o jsonpath='{.status.addresses[0].value}')
```

In the travel control dashboard, use the sliders to change the requests for each travel locale. We need this to generate traffic
between the different services in the service mesh.

![travel-control-dashboard](https://validatedpatterns.io/images/travelops/ossm-travelops-controlapp.png)

1. Get the route to the kiali dashboard and log in using kubeadmin (or other credentialed user)

```shell
KIALI=https://$(oc get route kiali -n istio-system -o jsonpath={.spec.host})
```

1. Check the mTLS configuration for the Mesh

```shell
oc get peerauthentication -o jsonpath='{.items[*].spec.mtls.mode}' -n istio-system
```

The response should be `STRICT`

1. Within the dashboard verify that you see the following in the travel-agency, travel-control and travel-portal application contexts:

- Each application (travel-agency, travel-control and travel-portal) should have a green check mark next number of applications.

## Conclusion

The kiali dashboard shows us that our travelops applications are configured correctly for mTLS and properly joined to the service mesh. This test plan confirms that the deployed configuration is working as expected.
