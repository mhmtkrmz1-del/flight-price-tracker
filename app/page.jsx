import fs from "fs/promises";
import path from "path";

async function getPriceData() {
  const filePath = path.join(process.cwd(), "data", "prices.json");
  const raw = await fs.readFile(filePath, "utf8");
  return JSON.parse(raw);
}

function buildSummaryRows(routes) {
  return routes.map((route) => {
    const pegasusPrices = route.airlines.Pegasus || [];
    const ajetPrices = route.airlines.AJet || [];

    const pegasusMin = Math.min(...pegasusPrices);
    const ajetMin = Math.min(...ajetPrices);

    const pegasusMinIndex = pegasusPrices.indexOf(pegasusMin);
    const ajetMinIndex = ajetPrices.indexOf(ajetMin);

    const pegasusDate = route.dates[pegasusMinIndex];
    const ajetDate = route.dates[ajetMinIndex];

    const bestAirline = pegasusMin <= ajetMin ? "Pegasus" : "AJet";
    const bestDate = pegasusMin <= ajetMin ? pegasusDate : ajetDate;
    const bestPrice = pegasusMin <= ajetMin ? pegasusMin : ajetMin;

    return {
      direction: route.direction,
      from: route.from,
      to: route.to,
      pegasusDate,
      pegasusPrice: pegasusMin,
      ajetDate,
      ajetPrice: ajetMin,
      bestAirline,
      bestDate,
      bestPrice,
    };
  });
}

function buildDetailRows(routes) {
  return routes.flatMap((route) => [
    {
      airline: "Pegasus",
      direction: route.direction,
      from: route.from,
      to: route.to,
      dates: route.dates,
      prices: route.airlines.Pegasus || [],
    },
    {
      airline: "AJet",
      direction: route.direction,
      from: route.from,
      to: route.to,
      dates: route.dates,
      prices: route.airlines.AJet || [],
    },
  ]);
}

export default async function Page() {
  const data = await getPriceData();
  const summaryRows = buildSummaryRows(data.routes || []);
  const detailRows = buildDetailRows(data.routes || []);

  const pageStyle = {
    background: "#f8fafc",
    minHeight: "100vh",
    fontFamily: "Arial, sans-serif",
    padding: "32px 20px 60px",
    color: "#0f172a",
  };

  const containerStyle = {
    maxWidth: 1450,
    margin: "0 auto",
  };

  const cardStyle = {
    background: "#ffffff",
    border: "1px solid #e2e8f0",
    borderRadius: 18,
    padding: 20,
    marginBottom: 24,
    boxShadow: "0 1px 2px rgba(0,0,0,0.04)",
  };

  const tableStyle = {
    width: "100%",
    borderCollapse: "collapse",
    fontSize: 15,
  };

  const thStyle = {
    textAlign: "left",
    padding: "12px 10px",
    borderBottom: "1px solid #cbd5e1",
    background: "#f1f5f9",
    whiteSpace: "nowrap",
  };

  const tdStyle = {
    padding: "10px 10px",
    borderBottom: "1px solid #e2e8f0",
    whiteSpace: "nowrap",
  };

  return (
    <main style={pageStyle}>
      <div style={containerStyle}>
        <h1 style={{ fontSize: 42, margin: "0 0 8px" }}>Uçuş Fiyat Takip Paneli</h1>
        <p style={{ margin: "0 0 8px", color: "#475569", fontSize: 16 }}>
          Üstte her rota için en ucuz tarih özeti, altta her hava yolu için tüm tarihlerdeki fiyatlar.
        </p>
        <p style={{ margin: "0 0 24px", color: "#64748b", fontSize: 14 }}>
          Son güncelleme: {data.updatedAt || "Bilinmiyor"}
        </p>

        <section style={cardStyle}>
          <h2 style={{ marginTop: 0, marginBottom: 16, fontSize: 24 }}>En Ucuz Tarih Özeti</h2>
          <div style={{ overflowX: "auto" }}>
            <table style={tableStyle}>
              <thead>
                <tr>
                  <th style={thStyle}>Yön</th>
                  <th style={thStyle}>Nereden</th>
                  <th style={thStyle}>Nereye</th>
                  <th style={thStyle}>Pegasus en ucuz tarih</th>
                  <th style={thStyle}>Pegasus fiyat</th>
                  <th style={thStyle}>AJet en ucuz tarih</th>
                  <th style={thStyle}>AJet fiyat</th>
                  <th style={thStyle}>Genel en ucuz</th>
                  <th style={thStyle}>Tarih</th>
                  <th style={thStyle}>Fiyat</th>
                </tr>
              </thead>
              <tbody>
                {summaryRows.map((row, i) => (
                  <tr key={i}>
                    <td style={tdStyle}>{row.direction}</td>
                    <td style={tdStyle}>{row.from}</td>
                    <td style={tdStyle}>{row.to}</td>
                    <td style={tdStyle}>{row.pegasusDate}</td>
                    <td style={tdStyle}>€{row.pegasusPrice}</td>
                    <td style={tdStyle}>{row.ajetDate}</td>
                    <td style={tdStyle}>€{row.ajetPrice}</td>
                    <td style={{ ...tdStyle, fontWeight: "bold", color: "#0f766e" }}>{row.bestAirline}</td>
                    <td style={{ ...tdStyle, fontWeight: "bold" }}>{row.bestDate}</td>
                    <td style={{ ...tdStyle, fontWeight: "bold", background: "#fef9c3" }}>€{row.bestPrice}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section style={cardStyle}>
          <h2 style={{ marginTop: 0, marginBottom: 8, fontSize: 24 }}>Detaylı Fiyat Listesi</h2>
          <p style={{ marginTop: 0, color: "#64748b" }}>
            Her satır bir hava yolunu gösterir. En ucuz fiyat sarı ile vurgulanır.
          </p>

          {detailRows.map((row, rowIndex) => {
            const minPrice = Math.min(...row.prices);

            return (
              <div
                key={rowIndex}
                style={{
                  marginTop: 20,
                  marginBottom: 28,
                  border: "1px solid #e2e8f0",
                  borderRadius: 14,
                  overflowX: "auto",
                }}
              >
                <div
                  style={{
                    background: "#f8fafc",
                    padding: "12px 14px",
                    borderBottom: "1px solid #e2e8f0",
                    fontWeight: "bold",
                    fontSize: 16,
                  }}
                >
                  {row.airline} — {row.direction} — {row.from} → {row.to}
                </div>

                <table style={tableStyle}>
                  <thead>
                    <tr>
                      <th style={thStyle}>Hava yolu</th>
                      <th style={thStyle}>Nereden</th>
                      <th style={thStyle}>Nereye</th>
                      <th style={thStyle}>Tarih</th>
                      <th style={thStyle}>Fiyat</th>
                    </tr>
                  </thead>
                  <tbody>
                    {row.dates.map((date, i) => {
                      const isMin = row.prices[i] === minPrice;

                      return (
                        <tr key={i}>
                          <td style={tdStyle}>{row.airline}</td>
                          <td style={tdStyle}>{row.from}</td>
                          <td style={tdStyle}>{row.to}</td>
                          <td style={tdStyle}>{date}</td>
                          <td
                            style={{
                              ...tdStyle,
                              fontWeight: isMin ? "bold" : "normal",
                              background: isMin ? "#fde047" : "transparent",
                            }}
                          >
                            €{row.prices[i]}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            );
          })}
        </section>
      </div>
    </main>
  );
}
