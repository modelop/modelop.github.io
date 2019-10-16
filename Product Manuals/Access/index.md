---
title: "Access"
---
# Access

ModelOp Center Access is provides some basic security, wrapping the ModelOp Center fleet behind an NGINX reverse-proxy, while at the same time providing a few methods for authorizing users.

To run Access, port 9000 must be exposed, and the `FASTSCORE_PROXY` environment variable must be set to either the `dashboard` or `frontman` proxy:

```
  access:
    image: fastscore/access:1.9
    ports:
      - "9000:9000"
    environment:
      FASTSCORE_PROXY: https://dashboard:8000
```

Configured in this way, access to port 8000 on the dashboard container will be restricted to those who know the username/password baked into Access (`admin`/`password` are the defaults).

The list of accepted usernames/passwords can be modified by mapping into the container a new .htpasswd file at the following location:

`/etc/apache2/.htpasswd`

This file can be created using the `htpasswd` utility:

https://httpd.apache.org/docs/2.4/programs/htpasswd.html

Access can additionally be configured to talk to an Active Directory server, and can also be configured for OAuth2 and Open ID Connect.
