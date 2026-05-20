# GitHub Actions CI Pipeline — Setup Guide

> **This guide assumes your project files are already ready.**  
> You should have these files in your project folder before starting:
>
> ```
> flask-ci-demo/
> ├── app.py
> ├── test_app.py
> ├── requirements.txt
> └── Dockerfile
> ```
>
> If any of these are missing, create them first before continuing.

---

## Table of Contents

1. [Step 1 — Create a GitHub Repository](#step-1--create-a-github-repository)
2. [Step 2 — Push Your Code to GitHub](#step-2--push-your-code-to-github)
3. [Step 3 — Create a Docker Hub Account and Access Token](#step-3--create-a-docker-hub-account-and-access-token)
4. [Step 4 — Add Secrets to Your GitHub Repository](#step-4--add-secrets-to-your-github-repository)
5. [Step 5 — Create the GitHub Actions Workflow](#step-5--create-the-github-actions-workflow)
6. [Step 6 — Push and Watch the Pipeline Run](#step-6--push-and-watch-the-pipeline-run)
7. [Step 7 — Verify the Image on Docker Hub](#step-7--verify-the-image-on-docker-hub)
8. [What Happens on Every Push](#what-happens-on-every-push)
9. [Troubleshooting](#troubleshooting)
10. [Glossary](#glossary)

---

## Step 1 — Create a GitHub Repository

1. Go to [https://github.com](https://github.com) and sign in.
2. Click the **green "New"** button in the top-left, or go to [https://github.com/new](https://github.com/new).
3. Fill in the form:
   - **Repository name:** `flask-ci-demo`
   - **Visibility:** Public or Private — both work
   - **Do NOT** check "Add a README file"
   - **Do NOT** check "Add .gitignore"
   - **Do NOT** check "Choose a license"
4. Click **"Create repository"** (green button at the bottom).
5. GitHub shows a page with setup instructions. **Leave this page open** — you will need the repository URL in the next step.

---

## Step 2 — Push Your Code to GitHub

Open your terminal inside the `flask-ci-demo` folder and run these commands one by one:

```bash
# Initialize a git repository in this folder
git init

# Tell git who you are (use your real name and email)
git config user.email "you@example.com"
git config user.name "Your Name"

# Stage all files for the first commit
git add .

# Create the first commit
git commit -m "initial commit: flask app + tests + dockerfile"

# Rename the default branch to main
git branch -M main

# Connect your local folder to the GitHub repository
# Replace YOUR_USERNAME with your actual GitHub username
git remote add origin https://github.com/YOUR_USERNAME/flask-ci-demo.git

# Push the code to GitHub
git push -u origin main
```

After `git push`, go back to your browser and refresh the GitHub repository page. You should see your files there: `app.py`, `test_app.py`, `requirements.txt`, `Dockerfile`.

> **Did git ask for a username and password?**  
> GitHub no longer accepts plain passwords for `git push`. You need a Personal Access Token.  
> Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic) → Generate new token.  
> Give it `repo` scope. Use that token as the password when git asks.

---

## Step 3 — Create a Docker Hub Account and Access Token

The CI pipeline needs permission to push images to Docker Hub. We give it that permission via an **access token** — not your real password.

### 3.1 Create a Docker Hub account

If you do not have one:
1. Go to [https://hub.docker.com](https://hub.docker.com)
2. Click **Sign Up**
3. Choose a username — this becomes part of your image name (e.g. `johndoe/flask-demo`)
4. Verify your email

### 3.2 Create an Access Token

1. Sign in to [https://hub.docker.com](https://hub.docker.com)
2. Click your profile picture → **"Account Settings"**
3. In the left sidebar click **"Security"**
4. Click the blue **"New Access Token"** button
5. Fill in the form:
   - **Description:** `github-actions-flask-demo`
   - **Access permissions:** select **"Read, Write, Delete"**
6. Click **"Generate"**
7. **IMPORTANT:** Copy the token immediately — it is shown only once.  
   It looks like: `dckr_pat_xxxxxxxxxxxxxxxxxxxxxxxxxxxx`
8. Save it somewhere temporary (Notepad, TextEdit) — you will need it in the next step.

---

## Step 4 — Add Secrets to Your GitHub Repository

Your CI workflow needs your Docker Hub username and token. You must **never put these directly in your code**. GitHub stores them as encrypted secrets instead.

### 4.1 Open Repository Settings

1. Go to your repository: `https://github.com/YOUR_USERNAME/flask-ci-demo`
2. Click the **"Settings"** tab (last tab in the navigation bar, gear icon)
3. In the left sidebar, find **"Security"** → click **"Secrets and variables"** → click **"Actions"**

You are now on the **"Actions secrets and variables"** page.

### 4.2 Add the first secret: `DOCKERHUB_USERNAME`

1. Click the green **"New repository secret"** button
2. Fill in:
   - **Name:** `DOCKERHUB_USERNAME`
   - **Secret:** your Docker Hub username (e.g. `johndoe`)
3. Click **"Add secret"**

### 4.3 Add the second secret: `DOCKERHUB_TOKEN`

1. Click **"New repository secret"** again
2. Fill in:
   - **Name:** `DOCKERHUB_TOKEN`
   - **Secret:** paste the access token from Step 3.2 (starts with `dckr_pat_`)
3. Click **"Add secret"**

### 4.4 Verify

You should now see two secrets listed:
```
DOCKERHUB_TOKEN       Updated just now
DOCKERHUB_USERNAME    Updated just now
```

> **Can I read the secrets back?** No — GitHub masks all values permanently.  
> If you lose the token, generate a new one on Docker Hub and update the secret here.

---

## Step 5 — Create the GitHub Actions Workflow

GitHub Actions looks for pipeline files inside a specific folder: `.github/workflows/`.

### 5.1 Create the folder

In your terminal (inside `flask-ci-demo`):

```bash
# macOS / Linux
mkdir -p .github/workflows

# Windows (PowerShell)
New-Item -ItemType Directory -Force -Path .github\workflows
```

### 5.2 Create the workflow file

Create a file at `.github/workflows/ci.yml` and paste this exact content:

```yaml
name: CI Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  IMAGE_NAME: ${{ secrets.DOCKERHUB_USERNAME }}/flask-demo

jobs:

  # ── Job 1: Install dependencies and run tests ─────────────────────────────
  test:
    name: Build & Test
    runs-on: ubuntu-latest

    steps:
      - name: Checkout source code
        uses: actions/checkout@v4

      - name: Set up Python 3.12
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Cache pip packages
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: pip-${{ hashFiles('requirements.txt') }}

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run tests
        run: pytest test_app.py -v


  # ── Job 2: Build and push Docker image ────────────────────────────────────
  docker:
    name: Docker Build & Push
    runs-on: ubuntu-latest
    needs: test
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'

    steps:
      - name: Checkout source code
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Build and push image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: |
            ${{ env.IMAGE_NAME }}:latest
            ${{ env.IMAGE_NAME }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Print image info
        run: |
          echo "Pushed: ${{ env.IMAGE_NAME }}:latest"
          echo "Pushed: ${{ env.IMAGE_NAME }}:${{ github.sha }}"
```

### 5.3 Understanding the key parts

**`on: push: branches: [main]`**  
The pipeline runs automatically whenever you push a commit to the `main` branch.

**`on: pull_request: branches: [main]`**  
Tests also run on pull requests — but the Docker push is skipped (it requires a direct push to main).

**`needs: test`**  
Job 2 (docker) will not start until Job 1 (test) finishes successfully. If any test fails, the Docker image is never built and Docker Hub never receives broken code.

**`${{ secrets.DOCKERHUB_USERNAME }}`**  
This reads the secrets you added in Step 4. GitHub replaces these with the real values at runtime and hides them in all logs.

**`tags: | ...:latest ...:${{ github.sha }}`**  
Two tags are pushed every time:
- `:latest` — always points to the newest successful build
- `:<commit-sha>` — an immutable tag tied to the exact commit (e.g. `:a3f5c8d...`), useful for tracing which code is running

---

## Step 6 — Push and Watch the Pipeline Run

### 6.1 Push the workflow file

```bash
git add .github/workflows/ci.yml
git commit -m "ci: add github actions pipeline"
git push
```

### 6.2 Open the Actions tab

1. Go to your repository on GitHub
2. Click the **"Actions"** tab (between "Pull requests" and "Projects")
3. You should see a workflow run titled **"CI Pipeline"** with an orange spinning circle — this means it is running right now

### 6.3 Watch the run

1. Click on the run title
2. You see two boxes: **"Build & Test"** and **"Docker Build & Push"**
3. Click **"Build & Test"** to expand it
4. Click any step (e.g. **"Run tests"**) to see the live log output

Expected log for the test step:
```
test_app.py::test_health_returns_200 PASSED
test_app.py::test_health_returns_ok PASSED
test_app.py::test_index_returns_200 PASSED
test_app.py::test_index_has_all_fields PASSED
test_app.py::test_random_number_in_range PASSED
test_app.py::test_random_word_length PASSED
test_app.py::test_random_word_is_lowercase_alpha PASSED
test_app.py::test_random_name_is_valid PASSED

8 passed in 0.16s
```

5. After Job 1 turns green, Job 2 starts automatically
6. Watch the **"Build and push image"** step — takes 1–2 minutes on first run

### 6.4 Both jobs pass

When both jobs show a green checkmark the full pipeline succeeded. The image is now on Docker Hub.

---

## Step 7 — Verify the Image on Docker Hub

1. Go to [https://hub.docker.com](https://hub.docker.com) and sign in
2. Click **"Repositories"** in the top navigation
3. Click on **`flask-demo`**
4. Click the **"Tags"** tab

You should see two tags:
```
latest        pushed X minutes ago    ~50 MB
a3f5c8d9...   pushed X minutes ago    ~50 MB   ← the commit SHA tag
```

### 7.1 Pull and run the image to verify (optional)

```bash
# Pull from Docker Hub
docker pull YOUR_DOCKERHUB_USERNAME/flask-demo:latest

# Run it locally
docker run -p 8080:8080 YOUR_DOCKERHUB_USERNAME/flask-demo:latest
```

Then open `http://localhost:8080/` in your browser — you should see the JSON response.

---

## What Happens on Every Push

After this setup, every time you push a commit to `main`:

```
git push
    │
    └─► GitHub Actions starts automatically (within ~5 seconds)
          │
          ├─► Job 1: Build & Test
          │     1. Checks out your code
          │     2. Installs Python 3.12
          │     3. Restores cached pip packages (fast if deps unchanged)
          │     4. pip install -r requirements.txt
          │     5. pytest test_app.py -v
          │        ✓ all tests pass → Job 1 succeeds
          │        ✗ any test fails → pipeline stops, Docker not touched
          │
          └─► Job 2: Docker Build & Push  (only after Job 1 succeeds)
                1. Checks out your code
                2. Sets up Docker Buildx
                3. Logs in to Docker Hub (using your secrets)
                4. docker build + docker push
                   Tags: :latest and :<commit-sha>
                5. Prints confirmation

Total time: ~2 minutes warm cache, ~4 minutes first run
```

---

## Troubleshooting

### "DOCKERHUB_USERNAME secret not found" or image name is empty

**Cause:** The secret name was mistyped.  
**Fix:** Go to Settings → Secrets and variables → Actions. Delete the secret and recreate it with the exact name `DOCKERHUB_USERNAME` (all caps, underscore).

---

### "unauthorized: incorrect username or password"

**Cause:** The `DOCKERHUB_TOKEN` secret contains the wrong value, or you used your real password instead of an access token.  
**Fix:** Generate a new access token on Docker Hub (Step 3.2) and update the `DOCKERHUB_TOKEN` secret (Step 4.3).

---

### "denied: requested access to the resource is denied"

**Cause:** The access token was created with read-only permissions.  
**Fix:** Delete the old token on Docker Hub and create a new one with **"Read, Write, Delete"** permissions.

---

### Tests pass locally but fail in the pipeline

**Cause:** Usually a dependency version mismatch.  
**Fix:** Make sure `requirements.txt` lists all libraries your tests use with pinned versions.

---

### Pipeline did not start after pushing

**Check these in order:**
1. The workflow file is at `.github/workflows/ci.yml` (double-check the path)
2. The `on: push: branches: [main]` matches your actual branch name (`main` vs `master`)
3. Check the Actions tab — there may be a YAML parse error shown there
4. YAML is sensitive to indentation — every level must be exactly 2 spaces, never tabs

---

### How to check if your YAML is valid

Paste the contents of `ci.yml` into [https://www.yamllint.com](https://www.yamllint.com). It shows you exactly which line has a syntax error.

---

## Glossary

| Term | Plain English |
|------|---------------|
| **CI (Continuous Integration)** | Every code push automatically triggers tests |
| **CD (Continuous Delivery)** | After tests pass, the app is automatically built and shipped |
| **Pipeline** | A sequence of automated steps that run in order |
| **Job** | A group of steps that runs on one machine. Multiple jobs can run in parallel |
| **Step** | A single task inside a job — either a shell command or a marketplace Action |
| **Action** | A pre-built reusable step from the GitHub marketplace (e.g. `actions/checkout@v4`) |
| **Runner** | The virtual machine that executes a job. `ubuntu-latest` = a fresh Ubuntu Linux VM |
| **Secret** | An encrypted variable stored in GitHub. Values are hidden in all logs |
| **Docker image** | A snapshot of your app and everything it needs to run |
| **Docker container** | A running instance of a Docker image |
| **Docker Hub** | A public registry where Docker images are stored and shared |
| **Tag** | A label on a Docker image version. `:latest` = newest. `:<sha>` = tied to a specific commit |
| **SHA** | A unique identifier for a git commit (e.g. `a3f5c8d9`). Every commit gets a different SHA |
| **`needs:`** | Makes one job wait for another to succeed before starting |
| **`if:`** | A condition that controls whether a job or step runs |
| **`pytest`** | A Python testing framework that finds and runs functions starting with `test_` |
| **`assert`** | Checks if something is true. If false, the test fails |
| **Access token** | A password substitute that can be scoped and revoked independently |

---

*End of guide. Continue with `GUIDE-LOCAL-DEPLOY.md` to add deployment to your local machine.*
