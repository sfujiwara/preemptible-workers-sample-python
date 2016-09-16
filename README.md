# Preemptible Workers Sample for Python

This is an example using preemptible instances for batch processing.

## Basic Usage

### Create Instance Group

```sh
sh create_instance_group.sh
```

### Add Tasks to Pull Queue

```sh
python add_pull_queues.py
```

App Engine から instance group をチェックする間隔はリースタイムよりも長くしないとだめ