const backendUrl = process.env.BACKEND_URL || "http://backend:8000";

async function getHealth() {
  try {
    const response = await fetch(`${backendUrl}/health`, { cache: "no-store" });
    if (!response.ok) {
      return { status: "unreachable" };
    }
    return await response.json();
  } catch {
    return { status: "unreachable" };
  }
}

export default async function HomePage() {
  const health = await getHealth();

  return (
    <main style={{ fontFamily: "system-ui, sans-serif", padding: "2rem" }}>
      <h1>VATRI Frontend</h1>
      <p>Frontend container scaffold is running.</p>
      <p>Backend health: <strong>{health.status || "unknown"}</strong></p>
    </main>
  );
}
