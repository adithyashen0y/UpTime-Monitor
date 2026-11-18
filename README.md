# Uptime-Monitor

Checks websites on a schedule and shows whether each one is UP or DOWN, with response time and uptime %.
Logs an alert when a site goes down or comes back up.

**Built with:** Python (Flask), SQLite, Docker, Docker Compose, Jenkins

**Planned:** PostgreSQL, Nginx, Discord alerts, AWS EC2, Kubernetes

## How it works

| Part | What it does |
| --- | --- |
| `web/` | Flask dashboard: add and delete sites, see the latest status and uptime % |
| `checker/` | Background worker: checks every site every `CHECK_INTERVAL` seconds and saves the result |
| `docker-compose.yml` | Runs both containers, which share one database through the `uptime-data` volume |
| `jenkins/` | Custom Jenkins image used for CI |
| `Jenkinsfile` | The CI pipeline |

## Run the app

```bash
docker compose up -d --build
```

Open <http://localhost:5000> and add a site.

Stop it with `docker compose down`. Your data is kept in the `uptime-data` volume.

## CI with Jenkins

Every new commit is checked automatically. Jenkins polls GitHub every 5 minutes and runs:

1. **Python syntax**: `py_compile` on all app code
2. **Static analysis**: `pyflakes` (unused imports, undefined names)
3. **Docker build**: validates `docker-compose.yml` and builds the images

### 1. Build the Jenkins image

The official Jenkins image doesn't include Python or Docker, so `jenkins/Dockerfile` adds them:

```bash
docker build -t my-jenkins ./jenkins
```

### 2. Run Jenkins

```bash
docker run -d \
  --name jenkins \
  -p 8080:8080 \
  -v jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  --group-add $(stat -c %g /var/run/docker.sock) \
  my-jenkins
```

- `jenkins_home` volume: keeps jobs, builds and users when the container is recreated
- `docker.sock`: lets Jenkins use the host's Docker engine to build images (Docker-out-of-Docker)
- `--group-add`: gives Jenkins permission to use that socket. `stat -c %g /var/run/docker.sock` prints the host's docker group ID.

### 3. Set up the job

1. Get the first-time password: `docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword`
2. Open <http://localhost:8080>, install the suggested plugins and create an admin user
3. **New Item** → **Pipeline** → Definition: **Pipeline script from SCM** → Git → this repo's URL → branch `*/main` → Script Path `Jenkinsfile`

> Sharing `docker.sock` gives the container full control of the host's Docker. That's fine on a personal machine, but don't do it on shared servers.
