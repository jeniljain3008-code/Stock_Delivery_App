import type { Metadata } from "next";
import "./globals.css";
import { Sidebar } from "@/components/sidebar";

export const metadata: Metadata = { title: "Smart Delivery Analytics", description: "NSE delivery-first swing trading analytics" };

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en" className="dark"><body><div className="min-h-screen lg:grid lg:grid-cols-[280px_1fr]"><Sidebar /> <main className="p-4 lg:p-8">{children}</main></div></body></html>;
}
