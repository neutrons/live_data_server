.. _unresponsive:

Unresponsive Testing Server
---------------------------

Issue
+++++
Pointing the web browser to http://testfixture02-test.ornl.gov/admin causes the page to **hang**, the adming page
never shows up.

**Diagnostics: faulty TLS (ssl) certs**

login to testfixture02-test.ornl.gov and examine the `nginx` logs

.. code-block:: bash

   $> ssh cloud@testfixture02-test.ornl.gov
   $> docker logs test-nginx-1
   SSL_CTX_use_PrivateKey("/etc/pki/wildcard.sns.gov.key") failed (SSL: error:0B080074:x509 certificate routines:X509_check_private_key:key values mismatch)
   nginx: [emerg] SSL_CTX_use_PrivateKey("/etc/pki/wildcard.sns.gov.key") failed (SSL: error:0B080074:x509 certificate routines:X509_check_private_key:key values mismatch)

The logs indicate a problem with the certificate files.

An additional test is to substitute the
`nginx.conf file for the testing environment <https://code.ornl.gov/sns-hfir-scse/deployments/livedata-deploy/-/blob/main/test/nginx.conf?ref_type=heads>`_
with the
`local environment one <https://github.com/neutrons/live_data_server/blob/b903a26232dcbccf9f974d522c6113094a0689f0/config/nginx/envlocal.conf>`_,
which does not contain SSL certificates. Don't forget to change
`the server name <https://github.com/neutrons/live_data_server/blob/b903a26232dcbccf9f974d522c6113094a0689f0/config/nginx/envlocal.conf#L4>`_
from `"localhost"` to `"testfixture02-test.ornl.gov"`.
Redeploy after this. If the  http://testfixture02-test.ornl.gov/admin (notice the `http` instead of `https`) app is
served now, then it's a problem of the secure connection.


**Diagnostics: upstream firewall policy**

If the prod or test servers are hosted on ORNL cloud, ensure that unsolicited incoming requests on ports 80 and 443 are allowed in the upstream firewall.
Navigate to https://orc-open.ornl.gov and select the security group rules for the hosted instance.
Check to see that Ingress ports 80(HTTP) and 443(HTTPS) are allowed for 0.0.0.0/0 all IPv4 hosts.  The following screenshot depicts the desired configuration.

.. image:: /developer/media/forward_rule_443.GIF
    :width: 800px
    :align: center
    :alt: forward rule in CADES management
