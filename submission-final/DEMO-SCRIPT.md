# PakAura Demo Script

A step-by-step demo script for hackathon judges to follow when evaluating the PakAura AI-Powered Task Management application.

---

## Prerequisites

Before starting the demo, ensure the following services are running:

- **Backend** running on `http://localhost:8000`
- **Frontend** running on `http://localhost:3000`
- A modern web browser (Chrome, Firefox, or Edge recommended)

---

## Demo Flow (5-7 minutes)

### Step 1: Registration

1. Open your browser and navigate to `http://localhost:3000`.
2. You will land on the login page.
3. Click the **"Register"** link to switch to the registration form.
4. Enter the following credentials:
   - **Email:** `demo@pakaura.com`
   - **Password:** `Demo1234!`
5. Click the **Register** button.
6. Observe the successful registration and automatic redirect to the dashboard.

---

### Step 2: Dashboard Overview

1. Point out the **stats cards** at the top of the dashboard:
   - Total Tasks
   - Completed Tasks
   - Progress percentage
2. Note the **empty state message** indicating no tasks have been created yet.
3. Locate the **dark/light theme toggle** in the header area.
4. Click it to switch between themes and demonstrate the UI adaptability.

---

### Step 3: Create Tasks

1. Locate the task input field on the dashboard.
2. Add the following tasks one at a time, pressing Enter or clicking the Add button after each:
   - `Buy groceries`
   - `Finish project report`
   - `Call dentist`
   - `Exercise for 30 minutes`
3. After each task is added, observe how the **stats cards update in real-time** (total count increments, progress recalculates).
4. Point out the **task animations** as new items appear in the list.

---

### Step 4: Task Management

1. **Complete a task:** Click the checkbox next to **"Buy groceries"** to mark it as complete.
   - Note the progress bar updates immediately.
   - The completed task count increments.
2. **Edit a task:** Click the edit button on **"Call dentist"** and change it to `Call dentist at 3pm`. Save the edit.
3. **Delete a task:** Click the delete button on **"Exercise for 30 minutes"** to remove it.
   - Note the total count decrements and progress recalculates.
4. **Uncomplete a task:** Click the checkbox on **"Buy groceries"** again to mark it as incomplete.
   - Observe the stats revert accordingly.

---

### Step 5: AI Assistant

1. Navigate to the **AI Assistant** page using the sidebar or navigation menu.
2. Try the **quick action buttons** if available on the interface.
3. In the chat input, type the following commands one at a time and observe the responses:

| Command | Expected Result |
|---|---|
| `show all my tasks` | Displays the current list of tasks |
| `add task read a book` | Creates a new task called "read a book" |
| `complete read a book` | Marks "read a book" as complete |
| `uncomplete read a book` | Marks "read a book" as incomplete again |
| `delete read a book` | Deletes the "read a book" task |
| `clear completed tasks` | Removes all tasks marked as completed |
| `help` | Shows the list of available commands |
| `hello` | Returns a general greeting response |

4. After each command, point out how the AI processes natural language and executes task management operations seamlessly.

---

### Step 6: Logout and Re-login

1. Click **Sign Out** in the navigation area.
2. Observe the redirect back to the login page.
3. Log back in using the same credentials:
   - **Email:** `demo@pakaura.com`
   - **Password:** `Demo1234!`
4. Verify that all previously created tasks **persist across sessions**, demonstrating proper backend data storage.

---

### Step 7: Technical Demo (Optional)

If time permits and judges are interested in the technical implementation:

1. Open a new browser tab and navigate to `http://localhost:8000/api/docs`.
2. Show the **Swagger UI** with all available API endpoints.
3. Highlight the following endpoint categories:
   - Authentication endpoints (register, login, logout)
   - Task CRUD endpoints (create, read, update, delete)
   - AI chatbot endpoint
4. Navigate to the **health endpoint** at `http://localhost:8000/health` to show the service status response.

---

## Key Talking Points

Use these talking points throughout the demo to highlight the strengths of the application:

- **Full-stack application with AI integration** -- React frontend, FastAPI backend, and Cohere-powered AI assistant working together as a cohesive product.
- **Cohere FREE tier** -- The AI assistant uses Cohere's free API tier, meaning there is zero cost for AI capabilities.
- **Demo mode** -- The AI assistant works without an API key by falling back to a pattern-matching demo mode, ensuring the app is always functional.
- **Kubernetes-ready deployment** -- The application includes Helm charts and Kubernetes manifests for production-grade container orchestration.
- **Clean, modern UI** -- Responsive design with dark/light theme support, smooth animations, and intuitive task management workflow.
- **Real-time updates** -- Stats and progress indicators update immediately as tasks are created, completed, edited, or deleted.
- **Data persistence** -- User data and tasks are stored securely in the backend database, surviving browser refreshes and re-logins.

---

## Troubleshooting

If any issues arise during the demo:

| Issue | Resolution |
|---|---|
| Frontend not loading | Verify the frontend is running: `npm start` in the frontend directory |
| Backend not responding | Verify the backend is running: `uvicorn main:app --reload` in the backend directory |
| AI assistant not responding | Check if the Cohere API key is configured; the app will fall back to demo mode if absent |
| Login fails after registration | Confirm the backend database is accessible and the registration completed successfully |
| Tasks not persisting | Verify the backend database connection is active |
