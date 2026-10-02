# TokenWise backend

This directory contains the runnable Python backend for TokenWise. It is derived from the SWE-Pruner architecture and adds TokenWise repository retrieval plus a SEAL-derived trained carbon estimator.

The large `model/model.safetensors` file is intentionally not packaged. From the project root, use:

```powershell
.\scripts\copy-model.ps1
.\scripts\setup.ps1
.\scripts\verify.ps1
.\scripts\run-backend.ps1
```

Runtime endpoints:

- `GET /health`
- `POST /prune`
- `POST /prune-workspace`
- `POST /estimate-carbon`

Repository-context mode currently indexes Python source files only.
