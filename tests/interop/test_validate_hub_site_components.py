import logging
import os
import re
import subprocess

import pytest
from ocp_resources.route import Route
from ocp_resources.storage_class import StorageClass
from openshift.dynamic.exceptions import NotFoundError
from validatedpatterns_tests.interop import application, components

from . import __loggername__

logger = logging.getLogger(__loggername__)

oc = os.environ["HOME"] + "/oc_client/oc"


@pytest.mark.test_validate_hub_site_components
def test_validate_hub_site_components(openshift_dyn_client):
    logger.info("Checking Openshift version on hub site")
    version_out = components.dump_openshift_version()
    logger.info(f"Openshift version:\n{version_out}")

    logger.info("Dump PVC and storageclass info")
    pvcs_out = components.dump_pvc()
    logger.info(f"PVCs:\n{pvcs_out}")

    for sc in StorageClass.get(dyn_client=openshift_dyn_client):
        logger.info(sc.instance)


@pytest.mark.validate_hub_site_reachable
def test_validate_hub_site_reachable(kube_config, openshift_dyn_client):
    logger.info("Check if hub site API end point is reachable")
    err_msg = components.validate_site_reachable(kube_config, openshift_dyn_client)
    if err_msg:
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg
    else:
        logger.info("PASS: Hub site is reachable")


@pytest.mark.check_pod_status_hub
def test_check_pod_status(openshift_dyn_client):
    logger.info("Checking pod status")
    projects = [
        "openshift-operators",
        "openshift-gitops-operator",
        "openshift-cluster-observability-operator",
        "openshift-opentelemetry-operator",
        "openshift-tempo-operator",
        "travel-agency",
        "travel-control",
        "travel-portal",
        "travelops-hub",
        "vault",
    ]
    err_msg = components.check_pod_status(openshift_dyn_client, projects)
    if err_msg:
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg
    else:
        logger.info("PASS: Pod status check succeeded.")


@pytest.mark.validate_argocd_reachable_hub_site
def test_validate_argocd_reachable_hub_site(openshift_dyn_client):
    logger.info("Check if argocd route/url on hub site is reachable")
    err_msg = components.validate_argocd_reachable(openshift_dyn_client)
    if err_msg:
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg
    else:
        logger.info("PASS: Argocd is reachable")


# @pytest.mark.validate_istio_ingressgateway_route
# def test_validate_istio_ingressgateway_route(openshift_dyn_client):
#     namespace = "istio-system"
#     logger.info("Check for the existence of the istio_ingressgateway route")
#     try:
#         for route in Route.get(
#             dyn_client=openshift_dyn_client,
#             namespace=namespace,
#             name="istio-ingressgateway",
#         ):
#             logger.info(route.instance.spec.host)
#     except NotFoundError:
#         err_msg = "istio-ingressgateway url/route is missing in istio-system namespace"
#         logger.error(f"FAIL: {err_msg}")
#         assert False, err_msg

#     logger.info("PASS: Found istio-ingressgateway route")


@pytest.mark.validate_kiali_route
def test_validate_kiali_route(openshift_dyn_client):
    namespace = "istio-system"
    logger.info("Check for the existence of the kiali route")
    try:
        for route in Route.get(
            dyn_client=openshift_dyn_client,
            namespace=namespace,
            name="kiali",
        ):
            logger.info(route.instance.spec.host)
    except NotFoundError:
        err_msg = "kiali url/route is missing in istio-system namespace"
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg

    logger.info("PASS: Found kiali route")


@pytest.mark.validate_mtls
def test_validate_mtls(openshift_dyn_client):
    peerauth = subprocess.run(
        [
            "oc",
            "get",
            "peerauthentication",
            "-o",
            "jsonpath='{.items[*].spec.mtls.mode}'",
            "-n",
            "istio-system",
        ],
        capture_output=True,
    )
    peerauth = peerauth.stdout.decode("utf-8")
    logger.info(f"peerauthentication: {peerauth}")
    if re.search("^'STRICT'$", peerauth):
        logger.info("PASS: Peerauthentication is STRICT.")
    else:
        err_msg = "Peerauthentication is not STRICT"
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg


@pytest.mark.validate_argocd_applications_health_hub_site
def test_validate_argocd_applications_health_hub_site(openshift_dyn_client):
    logger.info("Get all applications deployed by argocd on hub site")
    projects = ["openshift-gitops", "travelops-hub"]
    unhealthy_apps = application.get_argocd_application_status(
        openshift_dyn_client, projects
    )
    if unhealthy_apps:
        err_msg = "Some or all applications deployed on hub site are unhealthy"
        logger.error(f"FAIL: {err_msg}:\n{unhealthy_apps}")
        assert False, err_msg
    else:
        logger.info("PASS: All applications deployed on hub site are healthy.")
