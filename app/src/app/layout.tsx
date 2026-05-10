import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Base Scout",
  description: "Monitor Base ecosystem — new projects, narratives, trends",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
