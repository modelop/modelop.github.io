## Github Integration

FastScore can use Github repo as a storage backend.
In this case all assets are stored as plain files in single repo with a mandated directory structure.
Every change to asset (via CLI or API) immediately pushed to Github repo.
And vice versa - external changes to repo (via git client or Github web interface) are propagated to Model Manage.

### Configuration

To use repo as a storage your `db` section in `config.yaml` should look like this:
```yaml
db:
  type: git
  url: https://github.com/org/repo.git
  branch: master
  username: joe
  password: secret
```

* `type: git` tells FastScore to use Github as storage backend.
* `url` should point to your existing Github repo.
* `branch` tells which git branch to use.
* `username` is the name of your Github user with read/write access to repo.
* `password` Github user password in a plain text.

Only HTTPS URLs to repos are supported for now. With Vault integration SSH URLs will be supported and plaintext passwords in config will be gone.

### Repo directories structure

FastScore store its assets in the following directories:
```
attachments
models
schemas
sensors
streams
```

Each asset stored as a separate file with file name being an asset name and file extension being an asset type.
No assets of same kind could share the same name.
Attachments are stored in subdirs named same as the model name they are belong.

Example:
```
models\
  model1.py
  mymodel.R
attachments\
  model1\
    att1.zip
    mylib1.tgz
streams\
  input1.json
  out.json
```

Here, attachments in `attachments/model1` dir are belong to model `model1.py`.

### Github webhooks
To make FastScore aware of external changes to repo you can use Github webhooks.
To set up a webhook on GitHub, head over to the **Settings** page of your repo, and click on **Webhooks & services**. After that, click on **Add webhook**. Paste publicly accessible URL of your FastScore proxy instance into Payload URL:
```
https://<FASTSCORE_PROXY>/api/1/service/model-manage-1/1/git
```
