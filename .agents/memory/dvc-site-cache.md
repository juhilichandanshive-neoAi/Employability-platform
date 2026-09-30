---
name: DVC site cache in read-only environments
description: Replit workspace workaround for DVC's default site-cache path.
---

When running DVC in this workspace, its default site cache can resolve to
`/var/tmp/dvc`, which is read-only. Set `DVC_SITE_CACHE_DIR` to a writable
temporary location for the command. Changing `TMPDIR` alone does not redirect
this DVC site cache.

**Why:** A DVC pull failed before reaching the remote because it could not
create `/var/tmp/dvc`.

**How to apply:** Set `DVC_SITE_CACHE_DIR=/tmp/<project>-dvc-site-cache` for
DVC CLI commands. Check the command's remote/cache result separately after
resolving the local site-cache error.