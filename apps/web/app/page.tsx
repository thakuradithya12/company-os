const foundationItems = [
  {
    number: "01",
    title: "Task execution",
    description: "The durable task engine is not enabled in this bootstrap release.",
    status: "Not implemented",
  },
  {
    number: "02",
    title: "Agent workforce",
    description: "The eight approved role specifications are documented; no agent is running yet.",
    status: "Not enabled",
  },
  {
    number: "03",
    title: "Memory and knowledge",
    description: "Persistent company memory will be added in its approved platform work package.",
    status: "Not implemented",
  },
  {
    number: "04",
    title: "Approvals and controls",
    description: "Privileged actions remain disabled until authentication and policy controls exist.",
    status: "Not implemented",
  },
];

export default function HomePage() {
  return (
    <main className="app-shell">
      <aside className="sidebar" aria-label="Primary navigation">
        <a className="brand" href="#overview" aria-label="Company OS home">
          <span className="brand-mark">C</span>
          <span className="brand-copy">
            <strong>Company OS</strong>
            <small>Founder workspace</small>
          </span>
        </a>
        <div className="nav-label">WORKSPACE</div>
        <a className="nav-item active" href="#overview" aria-current="page">
          <span className="nav-icon">⌂</span> Overview
        </a>
        <div className="nav-label muted-label">PLANNED MODULES</div>
        <div className="nav-item disabled"><span className="nav-icon">◷</span> Tasks <span className="nav-status">Later</span></div>
        <div className="nav-item disabled"><span className="nav-icon">◎</span> Workforce <span className="nav-status">Later</span></div>
        <div className="nav-item disabled"><span className="nav-icon">▤</span> Knowledge <span className="nav-status">Later</span></div>
        <div className="nav-item disabled"><span className="nav-icon">↗</span> Opportunities <span className="nav-status">Later</span></div>
        <div className="sidebar-bottom">
          <span className="status-dot" aria-hidden="true" />
          <span>Foundation build</span>
          <span className="version">v0.1.0</span>
        </div>
      </aside>

      <section className="main-panel" id="overview">
        <header className="topbar">
          <div>
            <span className="eyebrow">COMPANY CONTROL CENTER</span>
            <h1>Build the operating foundation.</h1>
          </div>
          <span className="environment-pill"><span className="status-dot" /> Development</span>
        </header>

        <section className="welcome-block" aria-labelledby="welcome-heading">
          <div className="welcome-copy">
            <span className="step-kicker">CURRENT MILESTONE · PHASE 2</span>
            <h2 id="welcome-heading">One company. One control plane.</h2>
            <p>
              This is the initial web shell for Company OS. We are establishing repeatable setup,
              configuration validation, database migration tooling, and health checks before building
              the task engine or enabling agents.
            </p>
          </div>
          <div className="foundation-seal" aria-hidden="true">
            <span className="seal-orbit orbit-one" />
            <span className="seal-orbit orbit-two" />
            <span className="seal-core">C</span>
          </div>
        </section>

        <div className="section-heading">
          <div>
            <span className="eyebrow">ENGINEERING STATUS</span>
            <h2>Foundation work packages</h2>
          </div>
          <span className="quiet-tag">No live agent telemetry yet</span>
        </div>

        <section className="work-grid" aria-label="Foundation work packages">
          {foundationItems.map((item) => (
            <article className="work-card" key={item.number}>
              <div className="card-topline">
                <span className="card-number">{item.number}</span>
                <span className="state-pill">{item.status}</span>
              </div>
              <h3>{item.title}</h3>
              <p>{item.description}</p>
            </article>
          ))}
        </section>

        <footer className="page-footer">
          <span>Company OS</span>
          <span>Foundation environment · Live execution is not enabled</span>
        </footer>
      </section>
    </main>
  );
}
