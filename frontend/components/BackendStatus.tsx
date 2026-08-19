"use client";

import { useEffect, useState } from "react";

const AGENT_URL =
  process.env.NEXT_PUBLIC_AGENT_URL?.replace(/\/$/, "") || "http://localhost:8000";

type Health = {
  status: string;
  name: string;
  engine: string;
};

export default function BackendStatus() {
  const [state, setState] = useState<"checking" | "ok" | "down">("checking");

  useEffect(() => {
    let cancelled = false;
    fetch(`${AGENT_URL}/api/health`)
      .then((res) => res.json())
      .then((data: Health) => {
        if (!cancelled) setState(data.status === "ok" ? "ok" : "down");
      })
      .catch(() => {
        if (!cancelled) setState("down");
      });
    return () => {
      cancelled = true;
    };
  }, []);

  if (state === "checking") {
    return (
      <span className="status status-checking">
        Checking assistant&hellip;
      </span>
    );
  }
  if (state === "ok") {
    return (
      <span className="status status-ok">
        Assistant online (chat widget is active)
      </span>
    );
  }
  return (
    <span className="status status-down">
      Assistant offline &mdash; starting the backend may take up to 30s on first
      visit
    </span>
  );
}