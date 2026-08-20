import BackendStatus from "@/components/BackendStatus";
import ChatWidget from "@/components/ChatWidget";

const services = [
  {
    name: "General Dentistry",
    desc: "Check-ups, cleanings, fillings and preventive care for the whole family.",
    price: "from $120",
  },
  {
    name: "Cosmetic Dentistry",
    desc: "Teeth whitening, veneers and smile makeovers.",
    price: "from $250",
  },
  {
    name: "Orthodontics",
    desc: "Braces, retainers and clear aligners to straighten your smile.",
    price: "from $1,200",
  },
  {
    name: "Emergency Care",
    desc: "Walk-in care for toothaches, broken teeth and other urgent issues.",
    price: "same-day",
  },
];

const hours = [
  ["Monday – Friday", "9:00 AM – 6:00 PM"],
  ["Saturday", "10:00 AM – 2:00 PM"],
  ["Sunday", "Closed"],
];

export default function Home() {
  return (
    <>
      <div className="landing">
        <header className="site-header">
          <div className="logo" aria-hidden="true">
            &#129460;
          </div>
          <div>
            <h1>BrightSmile Dental Clinic</h1>
            <p className="tagline">A friendly, experienced team at your service</p>
          </div>
        </header>

        <section className="hero">
          <h2>We keep your smile bright</h2>
          <p>
            General, cosmetic and emergency dental care in a comfortable,
            modern clinic. Ask our online assistant about services, prices,
            opening hours or to book an appointment &mdash; just click the chat
            bubble in the bottom-right corner.
          </p>
          <BackendStatus />
        </section>

        <section className="section">
          <h2>Services &amp; prices</h2>
          <ul className="cards">
            {services.map((s) => (
              <li key={s.name} className="card">
                <h3>{s.name}</h3>
                <p>{s.desc}</p>
                <span className="price">{s.price}</span>
              </li>
            ))}
          </ul>
        </section>

        <section className="section">
          <h2>Opening hours</h2>
          <ul className="hours">
            {hours.map(([days, time]) => (
              <li key={days}>
                <span>{days}</span>
                <span>{time}</span>
              </li>
            ))}
          </ul>
        </section>

        <section className="section">
          <h2>Contact</h2>
          <address className="contact">
            <p>125 Main Street,<br />Springfield</p>
            <p>Phone: <a href="tel:+15550182">+1 555-0182</a></p>
            <p>Email: <a href="mailto:reception@brightsmileclinic.com">reception@brightsmileclinic.com</a></p>
          </address>
        </section>

        <footer className="site-footer">
          <p>
            This is a demo so you can try our AI assistant &mdash; ask it about
            prices, hours, or to book an appointment. Try it Now.
          </p>
        </footer>
      </div>
      <ChatWidget />
    </>
  );
}