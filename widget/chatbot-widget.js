/* BrightSmile floating chatbot widget (vanilla JS, no dependencies).
 *
 * Drop into any page (including a Next.js site) with:
 *   <script src="https://YOUR-AGENT-HOST/widget/chatbot-widget.js"></script>
 *
 * Optional config before the script tag:
 *   window.BrightSmileChatbot = { apiBase: "https://YOUR-AGENT-HOST" };
 */
(function () {
  "use strict";

  if (window.__BrightSmileChatbotLoaded) return;
  window.__BrightSmileChatbotLoaded = true;

  var config = Object.assign(
    {
      apiBase: "",
      title: "BrightSmile Dental Clinic",
      subtitle: "Typically replies instantly",
      botName: "BrightSmile Assistant",
    },
    window.BrightSmileChatbot || {}
  );

  var apiChat = (config.apiBase || "") + "/api/chat";
  var apiAppointments = (config.apiBase || "") + "/api/appointments";

  /* ---------- helpers ---------- */
  function el(tag, className, text) {
    var node = document.createElement(tag);
    if (className) node.className = className;
    if (text != null) node.textContent = text;
    return node;
  }

  function scrollDown() {
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  /* ---------- build DOM ---------- */
  var root = el("div");
  root.className = "bsc-widget";
  root.setAttribute("aria-live", "polite");

  root.innerHTML =
    '<button class="bsc-launcher" type="button" aria-label="Open chat">' +
    '  <svg class="bsc-chat-icon" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M12 3C6.5 3 2 6.9 2 11.7c0 2.6 1.3 4.9 3.4 6.4L4.7 21l3.6-1.8c1.1.3 2.3.5 3.7.5 5.5 0 10-3.9 10-8.7S17.5 3 12 3z"/></svg>' +
    '  <svg class="bsc-close-icon" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M18.3 5.7L12 12l6.3 6.3-1.4 1.4L10.6 13.4l-6.3 6.3-1.4-1.4L9.2 12 2.9 5.7l1.4-1.4 6.3 6.3 6.3-6.3z"/></svg>' +
    "</button>" +
    '<div class="bsc-panel" role="dialog" aria-label="Chat with BrightSmile Dental Clinic">' +
    '  <div class="bsc-header">' +
    '    <div class="bsc-header-avatar">&#128512;</div>' +
    '    <div class="bsc-header-info">' +
    "      <strong></strong><span></span>" +
    "    </div>" +
    '    <div class="bsc-header-actions">' +
    '      <button class="bsc-header-btn bsc-book-btn" type="button">Book</button>' +
    '      <button class="bsc-header-btn bsc-human-btn" type="button">Human</button>' +
    "    </div>" +
    "  </div>" +
    '  <div class="bsc-messages"></div>' +
    '  <div class="bsc-chips"></div>' +
    '  <form class="bsc-input-bar">' +
    '    <input type="text" placeholder="Type your message..." autocomplete="off" aria-label="Message" />' +
    '    <button class="bsc-send" type="submit" aria-label="Send">' +
    '      <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M2 21l21-9L2 3v7l15 2-15 2z"/></svg>' +
    "    </button>" +
    "  </form>" +
    "</div>";

  document.body.appendChild(root);

  var launcher = root.querySelector(".bsc-launcher");
  var panel = root.querySelector(".bsc-panel");
  var messagesEl = root.querySelector(".bsc-messages");
  var chipsEl = root.querySelector(".bsc-chips");
  var inputEl = root.querySelector(".bsc-input-bar input");
  var formEl = root.querySelector(".bsc-input-bar");
  var headerTitle = root.querySelector(".bsc-header-info strong");
  var headerSub = root.querySelector(".bsc-header-info span");

  headerTitle.textContent = config.title;
  headerSub.textContent = config.subtitle;

  /* ---------- state ---------- */
  var started = false;
  var open = false;

  /* ---------- message rendering ---------- */
  function addMessage(text, who) {
    var msg = el("div", "bsc-msg " + (who === "user" ? "bsc-user" : "bsc-bot"), text);
    messagesEl.appendChild(msg);
    scrollDown();
    return msg;
  }

  function addHumanCard(reply) {
    var card = el("div", "bsc-human");
    card.innerHTML =
      reply.replace(/\n/g, "<br>") +
      '<br><a class="bsc-human-btn" href="mailto:reception@brightsmileclinic.com">Email reception</a> ' +
      '<a class="bsc-human-btn" href="tel:+15550182">Call</a>';
    messagesEl.appendChild(card);
    scrollDown();
  }

  function showTyping() {
    var t = el("div", "bsc-typing");
    t.innerHTML = "<span></span><span></span><span></span>";
    t.dataset.typing = "1";
    messagesEl.appendChild(t);
    scrollDown();
    return t;
  }

  function hideTyping(t) {
    if (t && t.parentNode) t.parentNode.removeChild(t);
  }

  function setChips(labels, onClick) {
    chipsEl.innerHTML = "";
    labels.forEach(function (label) {
      var chip = el("button", "bsc-chip", label);
      chip.type = "button";
      chip.addEventListener("click", function () {
        sendMessage(label);
      });
      chipsEl.appendChild(chip);
    });
  }

  function clearChips() {
    chipsEl.innerHTML = "";
  }

  /* ---------- API calls ---------- */
  function post(url, body) {
    return fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }).then(function (res) {
      if (!res.ok) throw new Error("Request failed");
      return res.json();
    });
  }

  function sendMessage(text) {
    text = (text || "").trim();
    if (!text) return;
    addMessage(text, "user");
    inputEl.value = "";
    clearChips();
    var typing = showTyping();

    post(apiChat, { message: text })
      .then(function (data) {
        hideTyping(typing);
        if (data.handoff) {
          addHumanCard(data.reply);
        } else {
          addMessage(data.reply, "bot");
        }
        if (data.start_booking) {
          showBookingForm();
        }
      })
      .catch(function () {
        hideTyping(typing);
        addMessage("Sorry, I couldn't reach the assistant right now. Please try again in a moment.", "bot");
      });
  }

  /* ---------- booking form ---------- */
  function showBookingForm() {
    var form = el("form", "bsc-form");
    form.innerHTML =
      '<div><label for="bsc-f-name">Full name</label><input id="bsc-f-name" name="name" required /></div>' +
      '<div><label for="bsc-f-email">Email</label><input id="bsc-f-email" name="email" type="email" required /></div>' +
      '<div><label for="bsc-f-phone">Phone</label><input id="bsc-f-phone" name="phone" type="tel" required /></div>' +
      '<div><label for="bsc-f-date">Preferred date</label><input id="bsc-f-date" name="date" type="date" required /></div>' +
      '<div><label for="bsc-f-time">Preferred time</label><input id="bsc-f-time" name="time" type="time" required /></div>' +
      '<div><label for="bsc-f-reason">Reason for visit</label><input id="bsc-f-reason" name="reason" /></div>' +
      '<div class="bsc-form-actions">' +
      '  <button class="bsc-cancel" type="button">Cancel</button>' +
      '  <button class="bsc-submit" type="submit">Request appointment</button>' +
      "</div>" +
      '<div class="bsc-form-status"></div>';

    messagesEl.appendChild(form);
    scrollDown();

    form.querySelector(".bsc-cancel").addEventListener("click", function () {
      form.remove();
    });

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var statusEl = form.querySelector(".bsc-form-status");
      statusEl.textContent = "";
      var submitBtn = form.querySelector(".bsc-submit");
      submitBtn.disabled = true;
      submitBtn.textContent = "Sending...";

      var payload = {
        name: form.querySelector('[name="name"]').value,
        email: form.querySelector('[name="email"]').value,
        phone: form.querySelector('[name="phone"]').value,
        preferred_date: form.querySelector('[name="date"]').value,
        preferred_time: form.querySelector('[name="time"]').value,
        reason: form.querySelector('[name="reason"]').value,
      };

      post(apiAppointments, payload)
        .then(function (data) {
          form.remove();
          addMessage(data.message, "bot");
        })
        .catch(function () {
          submitBtn.disabled = false;
          submitBtn.textContent = "Request appointment";
          statusEl.className = "bsc-error";
          statusEl.textContent =
            "We couldn't submit your request right now. Please try again or contact reception at reception@brightsmileclinic.com.";
        });
    });
  }

  /* ---------- human handoff ---------- */
  function showHumanInfo() {
    addMessage("You can reach our reception team directly:\nEmail: reception@brightsmileclinic.com\nPhone: +1 555-0182", "bot");
  }

  /* ---------- open / close ---------- */
  function openWidget() {
    if (open) return;
    open = true;
    root.classList.add("bsc-open");
    if (!started) {
      started = true;
      setTimeout(function () {
        addMessage("Hello! Welcome to BrightSmile Dental Clinic. I can help you with our services, prices, opening hours, and appointment requests. How can I help you today?", "bot");
        setChips(["Opening hours", "Services & prices", "Book an appointment", "Talk to a human"]);
      }, 300);
    }
    inputEl.focus();
  }

  function closeWidget() {
    open = false;
    root.classList.remove("bsc-open");
  }

  launcher.addEventListener("click", function () {
    open ? closeWidget() : openWidget();
  });

  formEl.addEventListener("submit", function (e) {
    e.preventDefault();
    sendMessage(inputEl.value);
  });

  root.querySelector(".bsc-book-btn").addEventListener("click", function () {
    openWidget();
    showBookingForm();
  });

  root.querySelector(".bsc-human-btn").addEventListener("click", function () {
    openWidget();
    showHumanInfo();
  });
})();
