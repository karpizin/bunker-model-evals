# Download manifests

The `.urls` files use aria2 input-file syntax. Their `dir=./models/...` entries are intentionally relative so the manifests do not depend on a particular benchmark host or user account.

Run them from the desired data root:

```bash
mkdir -p "$HOME/bunker-data"
cd "$HOME/bunker-data"
aria2c --input-file /path/to/bunker-evals/configs/downloads/benchmark-wave-20261015.urls
```

Model weights are external inputs and must not be committed to this repository.
