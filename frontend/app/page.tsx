const backendUrl = process.env.BACKEND_URL || "http://backend:8000";

type HealthPayload = {
  status?: string;
};

async function getHealth(): Promise<HealthPayload> {
  try {
    const response = await fetch(`${backendUrl}/health`, { cache: "no-store" });
    if (!response.ok) {
      return { status: "unreachable" };
    }
    return (await response.json()) as HealthPayload;
  } catch {
    return { status: "unreachable" };
  }
}

export default async function HomePage() {
  const health = await getHealth();

  return (
    <main className="mx-auto min-h-screen max-w-3xl p-8">
      <h1 className="text-3xl font-semibold tracking-tight">VATRI Frontend</h1>
      <p className="mt-3 text-base text-slate-700">
        Frontend scaffold is running with TypeScript and Tailwind CSS.
      </p>
      <div className="mt-6 rounded-md border border-slate-200 bg-white p-4">
        <span className="text-sm text-slate-600">Backend health:</span>
        <strong className="ml-2 text-accent">{health.status || "unknown"}</strong>
      </div>
    </main>
  );
}
