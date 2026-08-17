# BrightSmile Dental Clinic — Chatbot Agent

A self-contained chatbot agent for the BrightSmile Dental Clinic website. It answers
questions from the approved clinic documentation and collects appointment requests.

- **Backend:** FastAPI (Python), rule-based intent engine (no LLM / no API costs)
- **Storage:** Supabase (`appointments` table)
- **Frontend:** dependency-free floating widget (`widget/`) that drops into the client's Next.js site

## Project layout

```
app/
  knowledge.py      Structured knowledge base (hours, services, prices, FAQs, contact)
  engine.py         Rule-based intent matching (all answers come from knowledge.py)
  config.py         Settings loaded from .env
  schemas.py        Pydantic request/response models
  supabase_db.py    Server-side Supabase insert (uses SUPABASE_SECRET_KEY)
  emailer.py        Optional Resend email (DORMANT until RESEND_API_KEY is set)
  routes.py         /api/chat and /api/appointments
widget/
  chatbot-widget.js + chatbot-widget.css   Floating chatbot (client deliverable)
frontend/
  index.html        Local test page only — NOT delivered to the client
supabase/
  migration.sql     SQL to paste into the Supabase SQL editor
tests/
  test_engine.py, test_api.py
main.py             FastAPI entry point
```

## Local setup

```bash
uv sync
uv run pytest                 # 28 tests
uv run uvicorn main:app --reload
```

- Test page: http://127.0.0.1:8000/demo (floating widget bottom-right)
- API health: http://127.0.0.1:8000/api/health
- `POST /api/chat` with `{"message": "what are your opening hours?"}`
- `POST /api/appointments` with `{name, email, phone, preferred_date, preferred_time, reason}`

## Environment variables (.env)

| Variable                  | Required | Purpose                                    |
| ------------------------- | -------- | ------------------------------------------ |
| `SUPABASE_URL`            | yes      | Supabase project URL                       |
| `SUPABASE_SECRET_KEY`     | yes      | Server-only key (`sb_secret_...`) for inserts |
| `RESEND_API_KEY`          | no       | Enables the receptionist email (dormant)   |
| `RECEPTIONIST_EMAIL`      | no       | Default `reception@brightsmileclinic.com`  |

The secret key is used only server-side and is never exposed to the browser.

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

Replace `AGENT-URL` with the deployed agent host. The widget:
- Answers from the approved documentation only (no outside/general knowledge)
- Never gives an exact filling price (uses the approved "$120 starting" message)
- Refuses medical advice and offers the human-handoff option
- Collects appointment requests and confirms they are **pending receptionist confirmation**
- Is fully responsive (bottom-sheet on mobile, panel on desktop)

## Email (dormant)

Appointment emails are currently dormant because no `RESEND_API_KEY` is configured.
Add the key to `.env` later to activate: each request is then emailed to the
receptionist in the format defined in `app/emailer.py`. Requests are always stored
in Supabase regardless.

## Intent coverage

greeting · hours · services · prices (per service) · dental filling (canned rule) ·
insurance · emergency · location · appointment needed · booking (form) · cancellation ·
medical advice (refuse + handoff) · human handoff · fallback (handoff)
