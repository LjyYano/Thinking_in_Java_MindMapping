# GPG Signing Setup for GitHub Actions

This document explains how to set up GPG signing for commits made by GitHub Actions to comply with protected branch requirements.

## Problem
The master branch requires verified signatures. GitHub Actions commits were being rejected with:
```
remote: error: GH006: Protected branch update failed for refs/heads/master.
remote: - Commits must have verified signatures.
```

## Solution
The workflow now uses GPG signing for all commits. To enable this, you need to configure GPG secrets in your repository.

## Setup Instructions

### Step 1: Generate a GPG Key

If you don't have a GPG key for the bot, generate one:

```bash
gpg --full-generate-key
```

When prompted:
- Select `(1) RSA and RSA`
- Key size: `4096` bits
- Expiration: Choose as appropriate (or 0 for no expiration)
- Real name: `github-actions[bot]`
- Email: `github-actions[bot]@users.noreply.github.com`
- Passphrase: Choose a strong passphrase (you'll need this later)

### Step 2: Export the GPG Key

List your GPG keys to find the key ID:
```bash
gpg --list-secret-keys --keyid-format=long
```

Export the private key (replace KEY_ID with your actual key ID):
```bash
gpg --armor --export-secret-keys KEY_ID
```

Copy the entire output including `-----BEGIN PGP PRIVATE KEY BLOCK-----` and `-----END PGP PRIVATE KEY BLOCK-----`.

### Step 3: Add Secrets to GitHub Repository

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add two secrets:
   - **Name:** `GPG_PRIVATE_KEY`
     - **Value:** Paste the entire GPG private key (including BEGIN and END lines)
   - **Name:** `GPG_PASSPHRASE`
     - **Value:** The passphrase you set when creating the key

### Step 4: Add GPG Public Key to GitHub Account

Export the public key:
```bash
gpg --armor --export KEY_ID
```

Add this public key to the GitHub account that will verify the commits:
1. Go to **GitHub Settings** → **SSH and GPG keys**
2. Click **New GPG key**
3. Paste the public key and save

### Step 5: Configure Branch Protection (If Needed)

Ensure the branch protection settings allow verified commits from the GitHub Actions bot:
1. Go to repository **Settings** → **Branches**
2. Edit the branch protection rule for `master`
3. Ensure "Require signed commits" is enabled
4. Consider adding the bot's GPG key to trusted signers if needed

## Verification

After setup, when the workflow runs:
1. The GPG key will be imported
2. Git will be configured to sign commits
3. Commits will be signed with the `-S` flag
4. The push to the protected branch will succeed

## Troubleshooting

### "No secret or public key" error
- Ensure `GPG_PRIVATE_KEY` secret is correctly formatted with BEGIN/END lines
- Check that there are no extra spaces or line breaks

### "gpg: signing failed: Inappropriate ioctl for device"
- This is handled by the `crazy-max/ghaction-import-gpg` action automatically

### Push still fails with signature error
- Verify the public key is added to the GitHub account
- Ensure the email in the GPG key matches the git config email
- Check that the key hasn't expired

## Alternative: Using GitHub App Token

If you prefer not to manage GPG keys manually, you can create a GitHub App with appropriate permissions. Note that GitHub App tokens still require GPG signing to comply with signed commit requirements - they do not automatically sign commits. However, a GitHub App can be configured with its own GPG key for better isolation and security. This approach requires creating and installing a GitHub App, which is more complex than using repository secrets.

## Workflow Changes Made

The workflow now includes:
1. **GPG key import step** using `crazy-max/ghaction-import-gpg@v6`
2. **Signed commit** using `git commit -S` flag
3. **Automatic git configuration** for signing (handled by the action)

This ensures all commits made by the workflow are properly signed and can be pushed to protected branches requiring verified signatures.
