import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Anime Tinder',
  description: 'Get anime recommendations by swiping',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
