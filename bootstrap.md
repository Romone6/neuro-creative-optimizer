# bootstrap.md

## Purpose
This file exists because the project pack must not quietly assume that TRIBE v2 or any other dependency is already present.

The coding agent is responsible for acquiring the external dependency stack itself.

## Non-negotiable rule
Treat the machine as a blank starting point.
The agent must download, install, validate, and document the setup.

## Required external dependency acquisition
### 1. Environment
The current public TRIBE v2 repository states **Python 3.11+**.
Create or validate a compatible environment first.

### 2. Repository acquisition
Acquire TRIBE v2 by cloning the public repository:
- source repo: `facebookresearch/tribev2`
- location inside project: `third_party/tribev2`

Preferred pattern:
```bash
git clone https://github.com/facebookresearch/tribev2.git third_party/tribev2
```

If the directory already exists, the agent should:
- check remote
- fetch latest refs if appropriate
- pin a known commit for reproducibility
- document the pinned revision

### 3. Installation
From the TRIBE repo, install in editable mode.
Base path for inference according to the public README:
```bash
pip install -e .
```

Optional extras only if the project needs them:
```bash
pip install -e ".[plotting]"
pip install -e ".[training]"
```

Do not install heavy extras by default unless they are required.

### 4. Pretrained asset resolution
The public README shows loading the pretrained model from Hugging Face through:
```python
from tribev2 import TribeModel
model = TribeModel.from_pretrained("facebook/tribev2", cache_folder="./cache")
```

The agent must implement a smoke test that attempts this load and records:
- success or failure
- cache location
- any auth issue
- any missing dependency issue
- any fallback mode activated

### 5. Smoke test requirement
The build is not considered bootstrapped until the agent runs a minimal test such as:
- initialize model
- create events dataframe from a supported modality
- call predict
- serialize status report

If a full inference example cannot run, the agent must still produce a precise diagnostic and keep the application running in degraded mode.

## Required bootstrap outputs
The bootstrap flow must emit a machine-readable status artifact, for example:
```json
{
  "python_version_ok": true,
  "tribe_repo_present": true,
  "tribe_commit": "<pinned_commit>",
  "tribe_install_ok": true,
  "pretrained_load_ok": true,
  "smoke_test_ok": true,
  "mode": "tribe_enabled"
}
```

If something fails, the mode might be:
- `tribe_degraded`
- `baseline_only`

## Product behavior under failure
If TRIBE bootstrap fails:
- do not crash the whole app
- do not lie and pretend it is working
- disable TRIBE-backed features behind a status gate
- continue with baseline scoring, audience conditioning, and revision flows
- surface the problem clearly in logs and setup status

## Required scripts
The project should include at minimum:
- `scripts/bootstrap.sh`
- `scripts/bootstrap.ps1`
- `scripts/smoke_test_tribe.py`

## Required Codex behavior
Codex should be instructed to:
1. scaffold repo
2. clone/download TRIBE v2
3. install dependencies
4. pin versions where sensible
5. run smoke test
6. record status
7. then continue building the application

That order matters.
