# 🧑‍💼 Employee Management System with AI Agent

A full-stack **CRUD application** for managing employees — powered by **React**, 
**Spring Boot**, and an intelligent **AI Agent** that lets you manage employees 
through natural language prompts.

> Instead of clicking buttons — just **type what you want**.

---

## 🎬 Demo (without the agent)


https://github.com/user-attachments/assets/d94b044c-f65f-4249-b1c7-6eedb54d8a20


--------
## 🤖 Demo AI Agent in Action


https://github.com/user-attachments/assets/b59f5b31-7a35-4c16-b6cf-08e59e7e79d5






---

## ✨ Features

### 👆 Manual CRUD (Traditional UI)
- ➕ Add new employees
- 👀 View all employees
- ✏️ Edit employee details
- 🗑️ Delete employees
- 🔍 Search & filter employees

### 🤖 AI Agent (Natural Language)
Just type what you want — the AI handles the rest:

| What You Type | What Happens |
|---|---|
| `show all employees` | Lists every employee |
| `find jessica` | Searches by name |
| `show all female employees` | Filters by gender |
| `add john doe email john@gmail.com` | Adds new employee |
| `delete jessica` | Asks confirmation → deletes |
| `update john's phone to 9876543210` | Asks confirmation → updates |

### 🛡️ Smart Confirmation Flow
- Destructive actions (delete/update) require **explicit confirmation**
- Type `yes` to confirm or `no` to cancel
- Memory persists across messages in same session

---

## 🛠️ Tech Stack

### Frontend
| Technology | Purpose |
|---|---|
| React | UI Framework |
| Tailwind CSS | Styling |
| Framer Motion | Animations |
| Axios | API calls |
| Lucide React | Icons |
| React Hot Toast | Notifications |

### Backend
| Technology | Purpose |
|---|---|
| Spring Boot | REST API |
| Spring Data JPA | Database ORM |
| MySQL / PostgreSQL | Database |
| Maven | Build tool |

### AI Layer
| Technology | Purpose |
|---|---|
| Python + FastAPI | AI microservice |
| LangGraph | Agent workflow graph |
| LangChain | LLM orchestration |
| Groq (Llama 3.3 70B) | Language model |
| httpx | Async HTTP calls |
| MemorySaver | Session memory |




