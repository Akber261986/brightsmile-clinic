"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

const AGENT_URL =
  process.env.NEXT_PUBLIC_AGENT_URL?.replace(/\/$/, "") || "http://localhost:8000";

type Appointment = {
  id: number;
  name: string;
  email: string;
  phone: string;
  preferred_date: string;
  preferred_time: string;
  reason: string | null;
  status: string;
  receptionist_message: string | null;
  created_at: string | null;
};

export default function AppointmentsPage() {
  const [items, setItems] = useState<Appointment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [rejectingId, setRejectingId] = useState<number | null>(null);
  const [rejectNote, setRejectNote] = useState("");
  const [busyId, setBusyId] = useState<number | null>(null);

  const load = useCallback(async () => {
    setError("");
    try {
      const res = await fetch(`${AGENT_URL}/api/appointments`);
      if (!res.ok) throw new Error("Could not load appointment requests.");
      const data: Appointment[] = await res.json();
      setItems(data);
    } catch {
      setError("Could not load appointment requests. Is the backend running?");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  function applyDecision(body: {
    appointment?: Appointment;
    email_sent?: boolean;
    message?: string;
  }) {
    if (body.appointment) {
      setItems((current) =>
        current.map((item) => (item.id === body.appointment!.id ? body.appointment! : item)),
      );
    }
    if (body.email_sent) {
      setNotice(body.message || "Email sent to the patient.");
    } else {
      setError(body.message || "The appointment was updated, but the email was not sent.");
    }
  }

  async function confirmAppointment(id: number) {
    setBusyId(id);
    setError("");
    setNotice("");
    try {
      const res = await fetch(`${AGENT_URL}/api/appointments/${id}/approve`, {
        method: "POST",
      });
      const body = await res.json().catch(() => ({}));
      if (!res.ok) {
        throw new Error(body.detail || "Could not confirm this request.");
      }
      applyDecision(body);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not confirm this request.");
    } finally {
      setBusyId(null);
    }
  }

  async function rejectAppointment(id: number) {
    const message = rejectNote.trim();
    if (!message) {
      setError("Please enter a message for the patient before rejecting.");
      return;
    }
    setBusyId(id);
    setError("");
    try {
      const res = await fetch(`${AGENT_URL}/api/appointments/${id}/reject`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
      });
      const body = await res.json().catch(() => ({}));
      if (!res.ok) {
        throw new Error(body.detail || "Could not reject this request.");
      }
      setItems((current) =>
        current.map((item) => (item.id === id ? body.appointment : item)),
      );
      setRejectingId(null);
      setRejectNote("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not reject this request.");
    } finally {
      setBusyId(null);
    }
  }

  return (
    <div className="landing appointments-page">
      <header className="site-header">
        <div className="logo" aria-hidden="true">
          &#129460;
        </div>
        <div>
          <h1>Appointment requests</h1>
          <p className="tagline">Review, confirm or reject pending bookings</p>
        </div>
        <Link className="nav-link" href="/">
          Back to clinic site
        </Link>
      </header>

      {error ? <p className="form-error">{error}</p> : null}
      {loading ? <p className="muted">Loading requests&hellip;</p> : null}
      {!loading && items.length === 0 && !error ? (
        <p className="muted">No appointment requests yet.</p>
      ) : null}

      <ul className="appointment-list">
        {items.map((item) => (
          <li key={item.id} className="appointment-card">
            <div className="appointment-card-head">
              <h2>{item.name}</h2>
              <span className={`badge badge-${item.status}`}>{item.status}</span>
            </div>
            <dl className="appointment-meta">
              <div>
                <dt>Email</dt>
                <dd>
                  <a href={`mailto:${item.email}`}>{item.email}</a>
                </dd>
              </div>
              <div>
                <dt>Phone</dt>
                <dd>{item.phone}</dd>
              </div>
              <div>
                <dt>Preferred date</dt>
                <dd>{item.preferred_date}</dd>
              </div>
              <div>
                <dt>Preferred time</dt>
                <dd>{item.preferred_time}</dd>
              </div>
              <div>
                <dt>Reason</dt>
                <dd>{item.reason || "Not provided"}</dd>
              </div>
              {item.receptionist_message ? (
                <div>
                  <dt>Reception message</dt>
                  <dd>{item.receptionist_message}</dd>
                </div>
              ) : null}
            </dl>

            {item.status === "pending" ? (
              <div className="appointment-actions">
                <button
                  type="button"
                  className="btn btn-confirm"
                  disabled={busyId === item.id}
                  onClick={() => void confirmAppointment(item.id)}
                >
                  Confirm
                </button>
                <button
                  type="button"
                  className="btn btn-reject"
                  disabled={busyId === item.id}
                  onClick={() => {
                    setRejectingId(item.id);
                    setRejectNote("");
                    setError("");
                  }}
                >
                  Reject
                </button>
              </div>
            ) : null}

            {item.status === "pending" && rejectingId === item.id ? (
              <div className="reject-box">
                <label htmlFor={`reject-note-${item.id}`}>
                  Message for the patient
                </label>
                <textarea
                  id={`reject-note-${item.id}`}
                  rows={4}
                  value={rejectNote}
                  onChange={(event) => setRejectNote(event.target.value)}
                  placeholder="Explain why the request cannot be confirmed…"
                />
                <div className="appointment-actions">
                  <button
                    type="button"
                    className="btn btn-reject"
                    disabled={busyId === item.id}
                    onClick={() => void rejectAppointment(item.id)}
                  >
                    Send rejection
                  </button>
                  <button
                    type="button"
                    className="btn btn-secondary"
                    disabled={busyId === item.id}
                    onClick={() => {
                      setRejectingId(null);
                      setRejectNote("");
                    }}
                  >
                    Cancel
                  </button>
                </div>
              </div>
            ) : null}
          </li>
        ))}
      </ul>
    </div>
  );
}
