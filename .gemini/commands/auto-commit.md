---
description: Analyze changes, generate a commit message, and push to remote
argument-hint: "Optional context or focus for the commit"
allowed-tools: Read, Bash(git:*)
---

You are an expert at creating clean, semantic commit messages. Follow the project's conventions and ensure all changes are safely pushed.

User input: $ARGUMENTS

## Step 1 — Analyze Changes
Run `git status` to identify modified, added, or deleted files.
Run `git diff HEAD` to see the actual code changes.
Review the last 3 commit messages with `git log -n 3` to match the project's style.

## Step 2 — Draft Commit Message
Generate a concise and descriptive commit message based on the analysis.
- Use the imperative mood (e.g., "Add feature" not "Added feature").
- Focus on the "why" and "what" changed.
- If $ARGUMENTS is provided, incorporate that context into the message.

## Step 3 — Stage and Commit
Run `git add .` to stage all changes.
Run `git commit -m "<commit_message>"` using the drafted message.

## Step 4 — Push to Remote
Run `git rev-parse --abbrev-ref HEAD` to get the current branch name.
Run `git push origin <branch_name>`.

## Step 5 — Report to User
Provide a summary of the action taken:
```
Branch:         <branch_name>
Commit Message: <commit_message>
Status:         Changes staged, committed, and pushed.
```
