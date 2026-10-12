import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { Header } from '@/components/layout/Header';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'POPULI - Smart Voting System',
  description: 'Portal Resmi Pemilihan Mahasiswa',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="id">
      <body className={`${inter.className} bg-[#121212] antialiased`}>
        {/* Header dipanggil di sini */}
        <Header />
        {children}
      </body>
    </html>
  );
}