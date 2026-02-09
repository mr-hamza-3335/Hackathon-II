---
id: 001
title: Create Demo Script for Hackathon Judges
stage: general
date: 2026-02-05
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: main
user: user
command: write-file
labels: ["demo", "documentation", "submission"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - submission-final/DEMO-SCRIPT.md
tests:
  - none
---

## Prompt

Write the file C:\Users\Mak Tech\Desktop\hackathon 2\submission-final\DEMO-SCRIPT.md

This is a step-by-step demo script for hackathon judges to follow when evaluating the PakAura AI-Powered Task Management app.

Structure it as:

# PakAura Demo Script

## Prerequisites
- Backend running on localhost:8000
- Frontend running on localhost:3000

## Demo Flow (5-7 minutes)

### Step 1: Registration
- Open http://localhost:3000
- Click "Register"
- Enter email: demo@pakaura.com, password: Demo1234!
- Show successful registration and auto-redirect to dashboard

### Step 2: Dashboard Overview
- Point out the stats cards (total, completed, progress)
- Note the empty state message
- Show dark/light theme toggle

### Step 3: Create Tasks
- Add tasks: "Buy groceries", "Finish project report", "Call dentist", "Exercise for 30 minutes"
- Show how stats update in real-time
- Show task animations

### Step 4: Task Management
- Complete "Buy groceries" by clicking checkbox
- Note the progress bar updates
- Edit "Call dentist" to "Call dentist at 3pm"
- Delete "Exercise for 30 minutes"
- Uncomplete "Buy groceries"

### Step 5: AI Assistant
- Navigate to AI Assistant page
- Try quick actions
- Type: "show all my tasks" - shows task list
- Type: "add task read a book" - creates new task
- Type: "complete read a book" - marks it complete
- Type: "uncomplete read a book" - marks incomplete
- Type: "delete read a book" - deletes it
- Type: "clear completed tasks" - removes completed
- Type: "help" - shows available commands
- Type: "hello" - general greeting

### Step 6: Logout & Re-login
- Click Sign Out
- Show redirect to login page
- Log back in with same credentials
- Show tasks persist

### Step 7: Technical Demo (optional)
- Show API docs at localhost:8000/api/docs
- Show Swagger UI
- Show health endpoint

## Key Talking Points
- Full-stack with AI integration
- Cohere FREE tier - no cost
- Demo mode works without API key
- Kubernetes-ready deployment
- Clean, modern UI

Do NOT use emojis. Keep it professional and clear.

## Response snapshot

Created the file `submission-final/DEMO-SCRIPT.md` containing a comprehensive, professional demo script for hackathon judges. The script includes: Prerequisites section, 7-step demo flow covering registration, dashboard overview, task creation, task management, AI assistant interaction, logout/re-login persistence, and optional technical demo. Also includes key talking points and a troubleshooting table. No emojis used; kept professional and clear throughout.

## Outcome

- Impact: Created demo script documentation for hackathon submission
- Tests: none
- Files: 1 created (submission-final/DEMO-SCRIPT.md)
- Next prompts: none
- Reflection: Straightforward documentation creation following the user's detailed structure

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
