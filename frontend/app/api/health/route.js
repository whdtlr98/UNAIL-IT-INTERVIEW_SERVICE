// src/app/api/health/route.js
export async function GET(req) {
  return new Response(
    JSON.stringify({ status: 'Healthy', timestamp: new Date().toISOString() }),
    {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    }
  );
}
