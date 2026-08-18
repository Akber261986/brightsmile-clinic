# BrightSmile Dental Clinic — Chatbot Agent

A chatbot agent for the BrightSmile Dental Clinic website. It answers patient
questions through an **LLM agent** bound by the clinic's approved documentation,
and collects appointment requests.

- **Backend:** FastAPI (Python) + **OpenAI Agents SDK** (`openai-agents`)
- **LLM:** Google Gemini via its OpenAI-compatible endpoint (configurable —
  any OpenAI-compatible model works). Automatic rule-based fallback if no LLM key is set.
- **Guardrails:** the agent's system prompt embeds the approved knowledge base
  and hard boundaries (exact-price rule for fillings, no medical advice, human
  handoff, booking flow). See `app/prompts.py`.
- **Storage:** Supabase (`appointments` table), receptionist email via Resend
- **Frontend:** dependency-free floating widget (`widget/`) that drops into the client's Next.js site

## Project layout

```
app/
  knowledge.py      Structured knowledge base (hours, services, prices, FAQs, contact)
  prompts.py        LLM system prompt with guardrails (built from knowledge.py)
  llm.py            OpenAI Agents SDK setup + structured reply (Gemini by default)
  engine.py         Rule-based fallback intent matcher (used when no LLM key)
  config.py         Settings loaded from .env
  schemas.py        Pydantic request/response models
  supabase_db.py    Server-side Supabase insert (uses SUPABASE_SECRET_KEY)
  emailer.py        Resend email (active only when RESEND_API_KEY is set)
  routes.py         /api/chat and /api/appointments
widget/
  chatbot-widget.js + chatbot-widget.css   Floating chatbot (client deliverable)
frontend/
  index.html        Local test page only — NOT delivered to the client
supabase/
  migration.sql     SQL to paste into the Supabase SQL editor
tests/
  test_engine.py, test_api.py, test_prompts.py
main.py             FastAPI entry point
```

## Local setup

```bash
uv sync
uv run pytest                 # 37 tests
uv run uvicorn main:app --reload
```

- Test page: http://127.0.0.1:8000/demo (floating widget bottom-right)
- API health: http://127.0.0.1:8000/api/health (reports `engine: llm`)
- `POST /api/chat` with `{"message": "what are your opening hours?"}` → returns `{intent, reply, handoff, start_booking}`
- `POST /api/appointments` with `{name, email, phone, preferred_date, preferred_time, reason}`

## Environment variables (.env)

| Variable            | Required | Purpose                                              |
| ------------------- | -------- | ---------------------------------------------------- |
| `SUPABASE_URL`      | yes      | Supabase project URL                                 |
| `SUPABASE_SECRET_KEY` | yes    | Server-only key (`sb_secret_...`) for inserts        |
| `GEMINI_API_KEY`    | yes*     | LLM key (Gemini or any OpenAI-compatible provider)   |
| `OPENAI_API_KEY`    | no       | Alternative LLM key (overrides Gemini if using OpenAI) |
| `LLM_BASE_URL`      | no       | Default `https://generativelanguage.googleapis.com/v1beta/openai/` |
| `LLM_MODEL`         | no       | Default `gemini-3.5-flash`                             |
| `RESEND_API_KEY`    | no       | Enables the receptionist email                        |
| `RECEPTIONIST_EMAIL`| no       | Default `reception@brightsmileclinic.com`            |
| `SENDER_EMAIL`      | no       | From address, default `onboarding@resend.dev`        |

\* Without an LLM key the agent runs on the rule-based fallback engine.

The secret keys are used only server-side and are never exposed to the browser.

## How the agent stays inside the clinic's rules

The system prompt (`app/prompts.py`) is generated from `app/knowledge.py` and
instructs the model to:

- answer **only** from the provided clinic information (no outside knowledge)
- give the exact listed price per service, but for dental fillings ALWAYS use
  the approved message: *"Dental fillings start at $120. The final cost may vary..."*
- never give medical advice — refuse politely and set `handoff=true`
- offer the human-handoff option (email/phone) for unknown info, medical
  questions, or when asked to speak with a human
- trigger the booking form (`start_booking=true`) when the patient wants an appointment

The chat response is returned as a structured object
`{reply, start_booking, handoff}` so the widget can render buttons and the
booking form correctly. If the LLM call fails, the API answers with a friendly
fallback and returns the old rule-based intent when no key is configured.

## Supabase setup (one-time)

1. Open the Supabase dashboard → **SQL Editor**.
2. Paste and run `supabase/migration.sql`.
3. Verify the `appointments` table appears under **Table Editor**.

Receptionist workflow: open the **Table Editor → appointments** and filter by
`status = 'pending'`. When email is enabled (add `RESEND_API_KEY`), each request is
also emailed automatically.

## Delivering to the client

The client only needs two files from `widget/` plus the deployed agent URL. On their
Next.js site, add to the layout (e.g. `app/layout.tsx`):

```tsx
import Script from "next/script";

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        {children}
        <Script src="https://AGENT-URL/widget/chatbot-widget.js" strategy="afterInteractive" />
      </body>
    </html>
  );
}
```

For non-Next.js sites, add before `</body>`:

```html
<link rel="stylesheet" href="https://AGENT-URL/widget/chatbot-widget.css" />
<script>
  window.BrightSmileChatbot = { apiBase: "https://AGENT-URL" };
</script>
<script src="https://AGENT-URL/widget/chatbot-widget.js"></script>
```

Replace `AGENT-URL` with the deployed agent host. The widget is fully responsive
(bottom-sheet on mobile, panel on desktop).

## Email

Set `RESEND_API_KEY` to activate receptionist emails. Note the default
`onboarding@resend.dev` sender can only deliver to your own Resend account email
(set `RECEPTIONIST_EMAIL` to it for testing). For production, verify a domain at
resend.com/domains and set `SENDER_EMAIL` to an address on it.