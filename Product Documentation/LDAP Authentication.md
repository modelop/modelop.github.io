---
title: "LDAP Authentication"
excerpt: "New in v1.4!"
---
Starting with FastScore v1.4, the FastScore Dashboard and Proxy support Microsoft Active Directory user authentication using [Vault](https://www.vaultproject.io/). To achieve this functionality, FastScore uses Vault to securely store the Active Directory configuration details. This page describes how to make use of authentication in FastScore.
[block:api-header]
{
  "title": "Connecting FastScore to Vault"
}
[/block]
This section assumes you already possess an existing Vault service. If you haven't configured Vault yet, [read the Vault configuration section below](#configuring-vault-in-docker).

Authentication in FastScore is achieved through the Dashboard service. Recall from the [Getting Started Guide](doc:getting-started-with-fastscore) that Dashboard is designed to serve as a proxy for the FastScore fleet's REST API, as well as a visual configuration and diagnostic aid. By default, authentication is not enabled in Dashboard. To enable it, set the following environment variables:
[block:parameters]
{
  "data": {
    "h-0": "Name",
    "h-1": "Default Value",
    "h-2": "Description",
    "h-3": "",
    "0-0": "`AUTH_SERVICE`",
    "0-1": "(none)",
    "0-2": "Set to `ldap` to enable authentication.",
    "1-0": "`VAULT_HOST`",
    "1-1": "`127.0.0.1`",
    "1-2": "The Vault server IP or hostname.",
    "2-0": "`VAULT_PORT`",
    "2-1": "`8200`",
    "2-2": "The Vault server port.",
    "3-0": "`VAULT_TOKEN`",
    "3-1": "(none)",
    "3-2": "Token which should be used for access to the Vault.",
    "4-0": "`VAULT_SSL`",
    "4-1": "`false`",
    "4-2": "Whether or not to use SSL with the Vault.",
    "6-0": "`VAULT_CACERT`",
    "6-1": "(none)",
    "6-2": "Path to the CA certificate.",
    "5-0": "`VAULT_SSL_VERIFY`",
    "5-1": "`false`",
    "5-2": "Whether to validate SSL requests."
  },
  "cols": 3,
  "rows": 7
}
[/block]
As seen from this table, the Dashboard must be provided with the Vault token and CA certificate to connect to the Vault. Generating the Vault token is discussed in the next section.

## Authentication in the CLI

The latest version of the FastScore CLI supports the authentication scheme described above. Usernames and passwords can be passed to the FastScore CLI's `connect` command. For example, the command
```
fastscore connect https://dashboard-ip:8000 foo:bar
```
attempts to authenticate with username "foo" and password "bar". If the password is omitted, the user will be prompted to enter it at the command line.

Note that the FastScore CLI will save the authentication secret to the file "`.fastscore`" located in the current working directory. 

## Authentication with the REST API

To authenticate via the REST API, use a POST request to `/1/login` with the username and password, e.g.,
```
POST /1/login HTTP/1.1
Host: localhost:3000
Content-Type: application/x-www-form-urlencoded
 
username=admin&password=admin
```
If the user has been successfully authenticated, the request will return **200 OK** together with cookies. After authorization, all subsequent requests should contain the cookie. 

If the REST API command fails, it may return the following error codes:
* 401: Returned if the user has no access to LDAP, or the wrong credentials were sent.
* 500: Returned if there's an LDAP server configuration error, or the server is not reachable.

## Authentication with the Dashboard

Entry point to configuration is https://localhost:3000/configuration
At first you will be automatically redirect to the create configuration page. After initial configuration users can change the LDAP configuration via the configuration page.

The user should create an admin password and set up the initial LDAP configuration. 
[block:image]
{
  "images": [
    {
      "image": [
        "https://files.readme.io/42f7e1b-LDAP_2.png",
        "LDAP 2.png",
        1019,
        785,
        "#35bbd2"
      ]
    }
  ]
}
[/block]

[block:image]
{
  "images": [
    {
      "image": [
        "https://files.readme.io/4c8bf11-LDAP_3.png",
        "LDAP 3.png",
        1045,
        802,
        "#35bbd3"
      ]
    }
  ]
}
[/block]
At the end of configuration create process the user will see a Root Token and Unseal Key for manual manipulating with Vault in case any errors occur or maintenance is needed. 

[block:image]
{
  "images": [
    {
      "image": [
        "https://files.readme.io/463968a-LDAP_1.png",
        "LDAP 1.png",
        1052,
        797,
        "#e3e4e4"
      ]
    }
  ]
}
[/block]
Below is the Admin login page.  
[block:image]
{
  "images": [
    {
      "image": [
        "https://files.readme.io/6fd4ed7-LDAP_4.png",
        "LDAP 4.png",
        972,
        739,
        "#34bcd4"
      ]
    }
  ]
}
[/block]

[block:api-header]
{
  "title": "Configuring Vault in Docker"
}
[/block]
In order to use authentication with the Dashboard, you need to have Vault running. Vault is a secure credentials repository, and it can be run either as a native binary, or in a Docker container. In this segment, we'll use the latter option. 

## Setting up the Vault Container

Use the following Docker-Compose file to start the Vault container:
[block:code]
{
  "codes": [
    {
      "code": "version: '2'\nservices:\n vault:\n    image: vault:latest\n    network_mode: \"host\"\n    tty: true\n    stdin_open: true\n    command: server\n    cap_add:\n      - IPC_LOCK\n # uncomment these lines if you're using aufs\n #   environment:\n #     SKIP_SETCAP: \"True\"\n    volumes:\n      - ./vault-config:/vault/config\n",
      "language": "yaml",
      "name": "vault-compose.yml"
    }
  ]
}
[/block]
Note that compose file links the local directory `vault-config` to the corresponding directory `/vault/config` in the container. This can be used to load configuration files and certificates into the Vault container. Additionally, the environment variable `SKIP_SETCAP` is currently commented out---uncomment this if you're using Docker's `aufs` filesystem (as of v0.6.3, there are some issues using `IPC_LOCK` on an `aufs` Docker filesystem).

Inside of the `vault` directory, create a subdirectory named `config` and put your Vault configuration file there. An example Vault configuration file might look like:
[block:code]
{
  "codes": [
    {
      "code": "{\n    \"backend\": {\n      \"file\": {\n        \"path\": \"/vault/file\"\n      }\n    },\n    \"listener\": {\n      \"tcp\": {\n        \"address\": \"0.0.0.0:8200\",\n        \"tls_disable\": 0,\n        \"tls_cert_file\": \"/vault/config/server.crt\",\n        \"tls_key_file\": \"/vault/config/server.key\"\n       }\n    },\n  \"default_lease_ttl\": \"168h\",\n  \"max_lease_ttl\": \"720h\",\n  \"disable_mlock\": true\n}\n",
      "language": "json",
      "name": "config.json"
    }
  ]
}
[/block]
In this configuration file, `server.crt` and `server.key` are your server's certificate and key---add these files to the `vault-config` folder as well.

Start the vault container with
```
docker-compose -f vault-compose.yml up -d
```

You can check that this worked with `docker-compose -f vault-compose.yml logs vault`, the output should look similar to:
```
Attaching to auth_vault_1
vault_1         | ==> Vault server configuration:
vault_1         | 
vault_1         |                  Backend: file
vault_1         |                      Cgo: disabled
vault_1         |               Listener 1: tcp (addr: "0.0.0.0:8200", cluster address: "")
vault_1         |                Log Level: info
vault_1         |                    Mlock: supported: true, enabled: false
vault_1         |                  Version: Vault v0.6.5
vault_1         |              Version Sha: 5d8d702f33b5fd965cbe8d6d0728295de813a196
vault_1         | 
vault_1         | ==> Vault server started! Log data will stream in below:
vault_1         | 
```

## Configuring Vault

The Vault container can be interacted with through both a CLI and a REST API. For simplicity, we'll focus on using the CLI. All CLI commands can be executed on both a local machine, or within the Vault container itself---we'll use `docker exec` to run the commands within the container.

Initialize the container with `vault init -key-threshold=1 -key-shares=1`:
```
docker-compose exec vault vault init -key-threshold=1 -key-shares=1
```
If this command succeeds, it should display the following:
```
Unseal Key 1: [Unseal Key]
Initial Root Token: [Root Token]

Vault initialized with 1 keys and a key threshold of 1. Please
securely distribute the above keys. When the Vault is re-sealed,
restarted, or stopped, you must provide at least 1 of these keys
to unseal it again.

Vault does not store the master key. Without at least 1 keys,
your Vault will remain permanently sealed.
```
Make sure to record `[Unseal Key]` and `[Root Token]`---we'll need them later! 

Use the `[Unseal Key]` to unseal the vault:
```
docker-compose exec vault vault unseal [Unseal Key]
```
The response will be similar to:
```
Sealed: false
Key Shares: 1
Key Threshold: 1
Unseal Progress: 0
Unseal Nonce: 
```

Now that the Vault is unsealed, authenticate using the `[Root Token]`:
```
docker-compose exec vault vault auth [Root Token]
```
You should see a message of successful authentication:
```
Successfully authenticated! You are now logged in.
token: [Root Token]
token_duration: 0
token_policies: [root]
```

Next, add the LDAP configuration information to the Vault. This is the information Dashboard will use to connect to your Active Directory server, so you'll need to customize it appropriately:
```
docker-compose exec vault vault write secret/ldap-configuration \
bindCredentials="password" \
bindDn="CN=mtwain,CN=Users,DC=odg,DC=local" \
searchBase="dc=odg,dc=local" \
searchFilter="(&(SamAccountName={{username}})" \
url="ldap://odgad.odg.local:3269"
```
If the command succeeds, the Vault will respond with
```
Success! Data written to: secret/ldap-configuration
```
In order to make this accessible from the Dashboard, we'll have to create an access policy. Our policy is configured with the file:
[block:code]
{
  "codes": [
    {
      "code": "path \"secret/ldap-configuration\" {\n    policy = \"read\"\n}\n \n \npath \"secret/ldap-configuration\" {\n    policy = \"read\"\n}\n",
      "language": "text",
      "name": "policy.hcl"
    }
  ]
}
[/block]
Set the policy for the `ldap-configuration` secret by copying the file `policy.hcl` to `vault-config` and running the command:
```
docker-compose exec vault vault policy-write dashboard-service-policy /vault/config/policy.hcl
```

The Dashboard will also need an LDAP certificate to connect to your LDAP Directory server over secure SSL-encrypted LDAP protocol. Copy this certificate over to the Vault container, either by placing it in the `vault-config` directory, or with `docker cp`:
```
docker cp ldap-ca-certificate.ca vault:/vault/config/
```
and write the certificate to the secret:
```
docker-compose exec vault vault write secret/ldap-ca-certificate \
value=@/vault/config/ldap-ca-certificate.ca
```

Finally, we enable `approle` and add the Dashboard policy from above:
```
docker-compose exec vault vault auth-enable approle
```
The response will be
```
Successfully enabled 'approle' at 'approle'!
```
Add the Dashboard service policy:
```
docker-compose exec vault vault write auth/approle/role/dashboard-service-role \ 
policies="dashboard-service-policy"
```
and capture the role ID and secret ID:
```
docker-compose exec vault vault read auth/approle/role/dashboard-service-role/role-id
docker-compose exec vault vault read -f \
auth/approle/role/dashboard-service-role/secret-id
```
The response will be:
```
Key     Value
---     -----
role_id [role_id]
```
and
```
Key                     Value
---                     -----
secret_id               [secret_id]
secret_id_accessor      [secret_id_accessor]
```

Add the `role_id` and `secret_id` to the Dashboard service in Vault:
```
docker-compose exec vault vault write auth/approle/login role_id=[role_id] secret_id=[secret_id]
```

# Authorized Users

In the [section on Configuring Vault](#configuring-vault), we have provided an example configuration to connect to Microsoft Active Directory. Other LDAP-enabled directories will be supported as well. We have stored the following details in Vault in order to properly authenticate and authorize users:

* Distinguished name of a user that has read access to your directory:
```
bindDn="CN=mtwain,CN=Users,DC=odg,DC=local"
```
* Password of the above user:
```
bindCredentials="password"
```
* Root of the directory tree where users reside:
```
searchBase="dc=odg,dc=local"
```
* The search filter defining which attribute maps to username and criteria for user authorization:
```
searchFilters="(&(SamAccountName={{username}})(memberOf=CN=fastscore-dashboard-users,CN=Users,DC=odg,DC=local))"
* LDAP URL defining the protocol (`ldap` or `ldaps`, server address, and port):
```
url="ldaps://odgad.odg.local:3269"
```

Based on the above configuration, only users that are members of `fastscore-dashboard-users` will be allowed to log in. This means that providing a valid username and password is not sufficient. You should also add the user to `fastscore-dashboard-users` in your directory.

You can also decide to use a different directory attribute as username. If, for example, you would like users to log in with their email addresses, you need to replace `"SamAccountName"` with `"mail"`:
```
searchFilter="$(mail={{username}})(memberOf=CN=fastscore-dashboard-users,CN=Users,DC=odg,DC=local))"
```