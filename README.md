# flask-jenkins-app

A small Flask API wired for a Jenkins CI/CD pipeline: lint, test, Docker build, smoke test, push, deploy.

## Project layout

```
flask-jenkins-app/
├── app/
│   ├── __init__.py        # application factory
│   ├── config.py          # dev / test / prod config
│   └── routes.py          # /, /health, /api/items
├── tests/
│   ├── conftest.py
│   └── test_app.py
├── scripts/deploy.sh      # run on the deploy host by Jenkins
├── wsgi.py                # gunicorn / local entry point
├── Dockerfile
├── Jenkinsfile
├── Makefile
├── requirements.txt       # runtime deps
├── requirements-dev.txt   # test + lint deps
└── setup.cfg              # flake8 + pytest config
```

## Run locally

```bash
python3 -m venv .venv && source .venv/bin/activate
make install
make test
make run            # http://localhost:5000
```

Endpoints: `GET /`, `GET /health`, `GET|POST /api/items`, `GET|DELETE /api/items/<id>`.

## Run in Docker

```bash
make docker-build
make docker-run
curl localhost:5000/health
```

## Jenkins setup

1. **Agent**: a node labelled `docker` with Docker and Python 3 (`python3-venv`) installed. The Jenkins user must be in the `docker` group.
2. **Credentials** (Manage Jenkins > Credentials):
   - `dockerhub-creds`: username + password/token for your registry
   - `deploy-ssh-key`: SSH private key for the deploy server (only needed to deploy)
3. **Edit the Jenkinsfile**: set `IMAGE_REPO` and `DEPLOY_HOST` in the `environment` block.
4. **Create the job**: New Item > Multibranch Pipeline > add your Git repo as a branch source. Script path: `Jenkinsfile`.
5. **Trigger on push**: add a GitHub/GitLab webhook to `http://<jenkins>/github-webhook/` (or `/project/<job>`), or use Poll SCM.

### Pipeline stages

| Stage | What it does |
|-------|--------------|
| Checkout | Pulls the branch |
| Setup Python | Creates a venv and installs dev requirements |
| Lint | `flake8` |
| Test | `pytest` with JUnit and coverage reports |
| Build Docker Image | Tags with build number and `latest` |
| Smoke Test Image | Starts the container and hits `/health` |
| Push Image | Only on `main` |
| Deploy | Only on `main` and when the `DEPLOY` parameter is ticked; SSHes to the host and runs `scripts/deploy.sh` |

## Notes

- The item store is in-memory, so data resets on restart and is per-worker under gunicorn. Swap in a database (e.g. RDS) for real use.
- Pin dependency versions (`pip freeze`) before production use for reproducible builds.
