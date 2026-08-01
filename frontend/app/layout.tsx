import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "FinAI CA — Financial Ratio Analysis",
  description: "Plain-language financial ratio analysis for small businesses",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="font-body">{children}</body>
    </html>
  );
}
