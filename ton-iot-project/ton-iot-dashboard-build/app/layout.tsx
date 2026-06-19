import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "TON_IoT Network Intrusion Detection Hub",
  description: "Interactive analytics dashboard for deep network traffic auditing and model comparisons.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
