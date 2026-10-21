import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Company OS | Control Center",
  description: "Founder-controlled AI company operating system.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
