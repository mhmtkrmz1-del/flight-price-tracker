"use client";

import { useEffect, useState } from "react";

const routes = [
  {
    from: "Köln",
    to: "Sabiha Gökçen",
    fromCode: "CGN",
    toCode: "SAW",
    dates: [
      "2026-07-11",
      "2026-07-12",
      "2026-07-13",
      "2026-07-14",
      "2026-07-15",
      "2026-07-16",
    ],
  },
];

function buildPayload(fromCode, toCode, date) {
  return {
    flightSearchList: [
      {
        departurePort: fromCode,
        arrivalPort: toCode,
        departureDate: date,
      },
    ],
    adultCount: 1,
    childCount: 0,
    infantCount: 0,
    currency: "EUR",
    dateOption: 1,
    bookingType: "BOOKING",
    operationCode: "TK",
    ffRedemption: false,
    expatPnr: false,
    personnelFlightSearch: false,
    totalPoints: null,
    affiliate: { id: null },
  };
}

function formatHumanDate(iso) {
  const d = new Date(iso);
  return d.toLocaleDateString("tr-TR", {
    day: "2-digit",
    month: "long",
    year: "numeric",
  });
}

export default function Page() {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [statusText, setStatusText] = useState("Hazır");

  async function fetchPegasusPrice(fromCode, toCode, date) {
    const response = await fetch("https://web.flypgs.com/pegasus/availability", {
      method: "POST",
      headers: {
        accept: "application/json, text/plain, */*",
        "content-type": "application/json",
        "x-platform": "web",
        "x-version": "1.75.0",
      },
      body: JSON.stringify(buildPayload(fromCode, toCode, date)),
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();

    const routeList = data?.departureRouteList || [];
    if (!routeList.length) return null;

    const dailyFlightList = routeList[0]?.dailyFlightList || [];
    if (!dailyFlightList.length) return null;

    const matched = dailyFlightList.find((x) => x.date === date) || dailyFlightList[0];
    const amount = matched?.cheapestFare?.amount;

    return typeof amount === "number" ? amount : null;
  }

  async function runCheck() {
    setLoading(true);
    setStatusText("Fiyatlar kontrol ediliyor...");
    const rows = [];

    for (const route of routes) {
      for (const date of route.dates) {
        try {
          const price = await fetchPegasusPrice(route.fromCode, route.toCode, date);

          rows.push({
            airline: "Pegasus",
            from: route.from,
            to: route.to,
            date,
            price: price ?? null,
            ok: price !== null,
            note: price !== null ? "Başarılı" : "Fiyat bulunamadı",
          });
        } catch (err) {
          rows.push({
            airline: "Pegasus",
            from: route.from,
            to: route.to,
            date,
            price: null,
            ok: false,
            note: `Hata: ${err.message}`,
          });
        }
      }
    }

    setResults(rows);
    setLoading(false);
    setStatusText("Kontrol tamamlandı");
  }

  useEffect(() => {
    runCheck();
  }, []);

  const validPrices = results.filter((r) => typeof r.price === "number");
  const cheapest = validPrices.length
    ? validPrices.reduce((min, item) => (item.price < min.price ? item : min), validPrices[0])
    : null;

  return (
    <main
      style={{
        minHeight: "100vh",
        background: "#f8fafc",
        fontFamily: "Arial, sans-serif",
        padding: 24,
        color: "#0f172a",
      }}
    >
      <div style={{ maxWidth: 1200, margin: "0 auto" }}>
        <h1 style={{ fontSize: 40, marginBottom: 10 }}>Uçuş Fiyat Takip Paneli</h1>

        <p style={{ color: "#475569", marginBottom: 8 }}>
          Bu sürüm fiyatları GitHub sunucusundan değil, doğrudan tarayıcından çekmeyi dener.
        </p>

        <p style={{ color: "#475569", marginBottom: 24 }}>
          Durum: <strong>{statusText}</strong>
        </p>

        <button
          onClick={runCheck}
          disabled={loading}
          style={{
            padding: "12px 18px",
            borderRadius: 10,
            border: "1px solid #cbd5e1",
            background: loading ? "#e2e8f0" : "#ffffff",
            cursor: loading ? "not-allowed" : "pointer",
            marginBottom: 24,
          }}
        >
          {loading ? "Kontrol ediliyor..." : "Yeniden kontrol et"}
        </button>

        <section
          style={{
            background: "#fff",
            border: "1px solid #e2e8f0",
            borderRadius: 16,
            padding: 20,
            marginBottom: 24,
          }}
        >
          <h2 style={{ marginTop: 0 }}>En Ucuz Bulunan Fiyat</h2>

          {cheapest ? (
            <div
              style={{
                padding: 16,
                borderRadius: 12,
                background: "#fef9c3",
                border: "1px solid #fde68a",
                fontSize: 18,
                fontWeight: "bold",
              }}
            >
              {cheapest.from} → {cheapest.to} — {formatHumanDate(cheapest.date)} — €{cheapest.price}
            </div>
          ) : (
            <div
              style={{
                padding: 16,
                borderRadius: 12,
                background: "#fee2e2",
                border: "1px solid #fecaca",
              }}
            >
              Henüz fiyat alınamadı. Tarayıcı CORS veya Pegasus koruması engelliyor olabilir.
            </div>
          )}
        </section>

        <section
          style={{
            background: "#fff",
            border: "1px solid #e2e8f0",
            borderRadius: 16,
            padding: 20,
          }}
        >
          <h2 style={{ marginTop: 0 }}>Detaylı Sonuçlar</h2>

          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr>
                  {["Hava yolu", "Nereden", "Nereye", "Tarih", "Fiyat", "Durum"].map((h) => (
                    <th
                      key={h}
                      style={{
                        textAlign: "left",
                        padding: 12,
                        borderBottom: "1px solid #cbd5e1",
                        background: "#f1f5f9",
                      }}
                    >
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {results.map((row, i) => {
                  const isCheapest =
                    cheapest &&
                    row.from === cheapest.from &&
                    row.to === cheapest.to &&
                    row.date === cheapest.date &&
                    row.price === cheapest.price;

                  return (
                    <tr key={i}>
                      <td style={{ padding: 12, borderBottom: "1px solid #e2e8f0" }}>{row.airline}</td>
                      <td style={{ padding: 12, borderBottom: "1px solid #e2e8f0" }}>{row.from}</td>
                      <td style={{ padding: 12, borderBottom: "1px solid #e2e8f0" }}>{row.to}</td>
                      <td style={{ padding: 12, borderBottom: "1px solid #e2e8f0" }}>
                        {formatHumanDate(row.date)}
                      </td>
                      <td
                        style={{
                          padding: 12,
                          borderBottom: "1px solid #e2e8f0",
                          background: isCheapest ? "#fde047" : "transparent",
                          fontWeight: isCheapest ? "bold" : "normal",
                        }}
                      >
                        {row.price !== null ? `€${row.price}` : "-"}
                      </td>
                      <td style={{ padding: 12, borderBottom: "1px solid #e2e8f0" }}>{row.note}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </main>
  );
}
