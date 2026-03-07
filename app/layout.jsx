export const metadata = {
  title: "Flight Price Tracker",
  description: "Uçuş fiyat takip paneli",
};

export default function RootLayout({ children }) {
  return (
    <html lang="tr">
      <body>{children}</body>
    </html>
  );
}
