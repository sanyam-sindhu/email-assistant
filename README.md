# Email Generation Assistant

This is a simple tool that writes professional emails for you. You give it three things: what the email is about, a few facts to include, and the tone you want. It then drafts the email using either Claude or GPT.

## What it does

You send it an intent (like "follow up after a client meeting"), a list of key facts that must appear in the email, and a tone (formal, casual, urgent, empathetic). It returns a finished email with a subject line, proper greeting, body, and sign off.

The same prompt is used for both Claude and GPT so you can fairly compare which model writes better emails.

## Setup

You need Python 3.11 or higher. First install the dependencies.

```
pip install -r requirements.txt
```

Then copy the example env file and fill in your API keys.

```
cp .env.example .env
```

Open .env and add your Anthropic and OpenAI keys. The models are already set to claude haiku and gpt 4o mini by default.

## Running the API

```
uvicorn app.main:app --reload --port 8000
```

Once it is running, go to http://localhost:8000/docs in your browser. You will see an interactive page where you can type in your inputs and get an email back instantly.

Or you can call it directly.

```
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "intent": "Follow up after a client meeting",
    "key_facts": ["Met on April 10th", "Discussed Q3 budget", "Need a decision by Friday"],
    "tone": "formal",
    "provider": "claude"
  }'
```

Change provider to "openai" to use GPT instead.

## Running the evaluation

This runs all 10 test scenarios against both models and scores every email on three metrics: how many facts made it in, how well the tone matched, and how clean and concise the writing is.

```
python -m eval.run_eval
```

It takes about 3 to 5 minutes. When it is done you will find the results in the results folder. raw_results.csv has every score, summary.json has the averages, and results/generated has each email as a plain text file so you can read them yourself.

## Project structure

The app folder has the prompt template, the generator that calls the APIs, and the FastAPI server. The eval folder has the 10 test scenarios with human written reference emails, the scoring logic, and the runner script. FINAL_REPORT.md has the full analysis of which model did better and why.
