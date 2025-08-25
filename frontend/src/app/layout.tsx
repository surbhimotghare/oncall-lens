import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "🔍 Oncall Lens - Incident Analyzer",
  description: "AI-powered incident analysis tool for on-call engineers",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="transition-colors duration-300">
      <body 
        className={`${inter.variable} font-sans antialiased bg-background text-foreground dark:bg-slate-900 dark:text-slate-100 transition-colors duration-300`}
        suppressHydrationWarning={true}
      >
        {children}
      </body>
    </html>
  );
}
