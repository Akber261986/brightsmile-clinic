"use client";

import { useEffect } from "react";

type WidgetConfig = {
  apiBase: string;
  title: string;
  subtitle: string;
};

const AGENT_URL =
  process.env.NEXT_PUBLIC_AGENT_URL?.replace(/\/$/, "") || "http://localhost:8000";

export default function ChatWidget() {
  useEffect(() => {
    if ((window as unknown as { __BrightSmileChatbotLoaded?: boolean }).__BrightSmileChatbotLoaded) return;

    const config: WidgetConfig = {
      apiBase: AGENT_URL,
      title: "BrightSmile Dental Clinic",
      subtitle: "Typically replies instantly",
    };
    (window as Window & { BrightSmileChatbot?: WidgetConfig }).BrightSmileChatbot =
      config;

    const href = document.createElement("link");
    href.rel = "stylesheet";
    href.href = "/widget/chatbot-widget.css";
    document.head.appendChild(href);

    const script = document.createElement("script");
    script.src = "/widget/chatbot-widget.js";
    script.async = true;
    document.head.appendChild(script);
  }, []);

  return null;
}