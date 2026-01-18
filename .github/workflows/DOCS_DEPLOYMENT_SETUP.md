# Documentation Deployment Setup Guide

This guide explains how to set up automatic deployment of ista documentation
to romanolab.org/software/ista.

## Overview

The deployment uses a two-repository workflow:
1. **ista repo**: Builds documentation on push to master
2. **romanolab.org repo**: Receives built docs and publishes to GitHub Pages

## Step 1: Create a Personal Access Token (PAT)

1. Go to GitHub Settings > Developer settings > Personal access tokens > Tokens (classic)
   - URL: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Configure the token:
   - **Note**: `ista-docs-deploy`
   - **Expiration**: Choose based on your preference (recommend 90 days or longer)
   - **Scopes**: Select `repo` (Full control of private repositories)
     - This is needed to trigger workflows in the romanolab.org repo
4. Click "Generate token"
5. **Copy the token immediately** - you won't see it again!

## Step 2: Add the Secret to ista Repository

1. Go to the ista repository on GitHub
2. Navigate to Settings > Secrets and variables > Actions
3. Click "New repository secret"
4. Configure:
   - **Name**: `DOCS_DEPLOY_TOKEN`
   - **Secret**: Paste the PAT you created in Step 1
5. Click "Add secret"

## Step 3: Add Workflow to romanolab.org Repository

Create a new file in your romanolab.org repository at:
`.github/workflows/receive-ista-docs.yml`

```yaml
# Receive and deploy ista documentation from the ista repository
#
# This workflow is triggered by the ista repository's build-docs workflow
# via repository_dispatch. It downloads the built docs and places them
# in the software/ista directory.

name: Deploy ista Documentation

on:
  repository_dispatch:
    types: [deploy-ista-docs]
  workflow_dispatch:  # Allow manual triggering

# Sets permissions of the GITHUB_TOKEN to allow deployment to GitHub Pages
permissions:
  contents: write
  pages: write
  id-token: write

jobs:
  deploy-ista-docs:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout romanolab.org repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Download ista docs artifact
        uses: dawidd6/action-download-artifact@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          repo: JDRomano2/ista
          workflow: build-docs.yml
          name: ista-docs
          path: software/ista
          # Get the most recent successful run
          workflow_conclusion: success
          # If triggered by dispatch, use the specific commit
          commit: ${{ github.event.client_payload.sha || '' }}

      - name: Commit and push changes
        run: |
          git config --local user.email "github-actions[bot]@users.noreply.github.com"
          git config --local user.name "github-actions[bot]"
          
          # Check if there are changes
          if git diff --quiet && git diff --staged --quiet; then
            echo "No changes to commit"
            exit 0
          fi
          
          git add software/ista
          git commit -m "Update ista documentation

          Source commit: ${{ github.event.client_payload.sha || 'manual trigger' }}
          Triggered by: ${{ github.event_name }}"
          git push
```

## Step 4: Configure romanolab.org Repository Permissions

For the workflow to download artifacts from the ista repository:

1. Go to ista repository Settings > Actions > General
2. Scroll to "Artifact and log retention"
3. Ensure artifacts are retained long enough for the deploy workflow
4. Scroll to "Workflow permissions"
5. Under "Access from outside collaborators and workflows", if you want
   public access to artifacts, enable it (or use a PAT as shown above)

**Alternative**: If the repositories are in the same organization or owned
by the same user, artifact downloads should work automatically with
`GITHUB_TOKEN`.

## Step 5: Prepare the romanolab.org Directory Structure

Ensure your romanolab.org repository has the following structure:

```
romanolab.org/
├── software/
│   └── ista/          # Created automatically by the workflow
│       └── index.html # Documentation will appear here
├── index.html         # Your main site
└── ...
```

If the `software/` directory doesn't exist, create it:
```bash
mkdir -p software/ista
echo "# Placeholder" > software/ista/.gitkeep
git add software/ista/.gitkeep
git commit -m "Add ista docs directory"
git push
```

## Step 6: Test the Deployment

1. In the ista repository, go to Actions tab
2. Select "Build Documentation" workflow
3. Click "Run workflow" > "Run workflow"
4. Wait for the build to complete
5. Check the romanolab.org repository - you should see a new workflow run
6. Once complete, visit https://romanolab.org/software/ista

## Troubleshooting

### Build fails with "Sphinx not found"
The workflow installs Sphinx automatically. Check the Python dependencies step.

### Dispatch fails with "Resource not accessible by integration"
- Verify the PAT has `repo` scope
- Verify the secret name is exactly `DOCS_DEPLOY_TOKEN`
- Verify the PAT hasn't expired

### Artifact download fails
- Check that the ista docs build completed successfully
- Verify artifact retention period
- If repos are in different organizations, you may need cross-repo permissions

### Docs don't appear at romanolab.org/software/ista
- Verify GitHub Pages is enabled for romanolab.org
- Check that the Pages source is set correctly (usually `main` branch, `/` root)
- Ensure the commit was pushed to the correct branch

## Manual Deployment (Fallback)

If automation fails, you can deploy manually:

```bash
# In ista repository
cd docs
make html

# Copy to romanolab.org repository
cp -r build/html/* /path/to/romanolab.org/software/ista/

# In romanolab.org repository
cd /path/to/romanolab.org
git add software/ista
git commit -m "Update ista documentation"
git push
```

## Security Notes

- The PAT should be kept secret and rotated periodically
- Consider using a fine-grained PAT with minimal permissions if available
- The workflow only triggers on pushes to master, not on PRs
- PR builds upload artifacts but don't trigger deployment
