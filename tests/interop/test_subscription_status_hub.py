import logging

import pytest
from validatedpatterns_tests.interop import subscription

from . import __loggername__

logger = logging.getLogger(__loggername__)


@pytest.mark.subscription_status_hub
def test_subscription_status_hub(openshift_dyn_client):
    # These are the operator subscriptions and their associated namespaces
    expected_subs = {
        "openshift-gitops-operator": ["openshift-gitops-operator"],
        "cluster-observability-operator": ["openshift-cluster-observability-operator"],
        "opentelemetry-product": ["openshift-opentelemetry-operator"],
        "tempo-product": ["openshift-tempo-operator"],
        "kiali-ossm": ["openshift-operators"],
        "servicemeshoperator3": ["openshift-operators"],
    }

    err_msg = subscription.subscription_status(
        openshift_dyn_client, expected_subs, diff=True
    )
    if err_msg:
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg
    else:
        logger.info("PASS: Subscription status check passed")
