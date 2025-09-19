# Contribution Guidelines

## 1. Repository Access

- This repository is **private** and access has already been granted to you.
- Make sure you are signed into GitHub with the account that has been given access.

---

## 2. Initial Setup

Run these commands once to clone the repository and set up your local workspace:

```bash
# Clone the repository to your system
git clone https://github.com/AnirudhDattu/SIH2025.git

# Move into the project folder
cd SIH2025

# Verify remote
git remote -v
```

---

## 3. Creating and Working on a Branch

Always work on a **separate branch** instead of `main`. This keeps the main branch stable.

```bash
# Fetch latest changes
git pull origin main

# Create and switch to a new branch
git checkout -b your-feature-branch-name
```

> Use a meaningful branch name, e.g., `feature-login-page`, `fix-navbar-bug`, or `update-readme`.

---

## 4. Making Changes

- Add your code, documentation, or assets.
- Stage the changes:

```bash
git add .
```

- Commit with a clear message:

```bash
git commit -m "Added login page with authentication"
```

---

## 5. Pushing Changes

Push your branch to GitHub:

```bash
git push origin your-feature-branch-name
```

---

## 6. Creating a Pull Request (PR)

1. Go to the repository on GitHub.
2. You’ll see a prompt to create a **Pull Request** for your branch.
3. Write a clear description of what you changed and why.
4. Submit the PR for review.

> The maintainer(s) will review, suggest changes (if any), and then merge into `main`.

---

## 7. Staying Updated

Always keep your branch updated with the latest changes from `main`:

```bash
git checkout main
git pull origin main
git checkout your-feature-branch-name
git merge main
```

---

## 8. Important Notes

- Do **not** commit directly to `main`.
- Ensure commits are meaningful and concise.
- Document your code where necessary.
- If you create empty folders, place a `.gitkeep` file inside them so Git tracks the directory.

---

Would you like me to also include a **GitHub Flow diagram** (visual workflow) in your README so your team can instantly grasp the branching/PR process?
