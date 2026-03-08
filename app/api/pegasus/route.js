export async function POST(req) {
  try {
    const body = await req.json();

    const response = await fetch(
      "https://web.flypgs.com/pegasus/availability",
      {
        method: "POST",
        headers: {
          "content-type": "application/json",
          accept: "application/json, text/plain, */*",
          "x-platform": "web",
          "x-version": "1.75.0",
          "user-agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
        },
        body: JSON.stringify(body),
      }
    );

    const text = await response.text();

    return new Response(text, {
      status: 200,
      headers: {
        "Content-Type": "application/json",
      },
    });
  } catch (err) {
    return new Response(JSON.stringify({ error: err.message }), {
      status: 500,
    });
  }
}
