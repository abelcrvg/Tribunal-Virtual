import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Tribunal Virtual",
  description: "Simulador jurídico baseado no Direito brasileiro.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="pt-BR">
      <body>{children}</body>
    </html>
  );
}
