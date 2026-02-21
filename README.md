# Computer Use Agent (CUA)

A **Computer Use Agent (CUA)** is an AI agent that can use a computer like a human — opening applications, clicking buttons, typing text, and navigating websites to complete tasks automatically.

This project implements a real-world CUA capable of controlling browsers and applications to perform end-to-end actions on behalf of a user.

Built using the **Google ADK (Agent Development Kit) framework**.

To understand **how the CUA works internally**, including its components and execution flow, see:
👉 [ARCHITECTURE.md](./ARCHITECTURE.md)

---

## Demo

### Agent opens a YouTube video from an Andrej Karpathy playlist

https://github.com/user-attachments/assets/159e06a9-0910-43ae-b979-0e3513512241



<!--
### Agent uploads a reel to a user’s Instagram account
https://github.com/user-attachments/assets/7f931bda-307b-47da-ae9f-4658ea55933f
-->
---

## Setup Instructions

1. Create a new `.env` file inside the `cua/` directory  
   Refer to `cua/.env.example` and paste your API keys.

2. Create and activate a virtual environment:
```bash
python -m venv .venv
.venv/Scripts/activate  # Windows
````

3. Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Running the Agent

From the root of the project:

1. Start the Omni server:

```bash
python -m omni.server
```

2. Run the CLI:

```bash
python cli.py
```

---

## License

This project is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**.

It includes code from the `trycua/cua/som` project, which is also licensed under AGPL-3.0.
The `trycua/cua/som` source code has been modified for use in this project.

