// components/layout/Header.tsx
'use client';

import React from 'react';
import Link from 'next/link';

export const Header: React.FC = () => {
  return (
    <header className="w-full bg-[#1c1c1e] border-b border-[#2c2c2e] px-6 py-3.5 flex justify-between items-center sticky top-0 z-50 text-white">
      {/* Brand Logo (Kotak Putih dengan Ikon Gedung Hitam) */}
      <Link href="/" className="flex items-center gap-3">
        <div className="w-9 h-9 bg-white rounded-xl flex items-center justify-center text-gray-900 font-bold shadow-sm">
          🏛️
        </div>
        <div className="flex flex-col">
          <span className="font-bold text-white tracking-tight leading-none text-sm">POPULI</span>
          <span className="text-[10px] text-gray-400 font-medium">POPULI</span>
        </div>
      </Link>

      {/* Badge Status Pemilihan (Di Tengah/Kanan) */}
      <div className="flex items-center gap-2 bg-[#2c2c2e]/60 border border-[#3a3a3c] text-gray-300 px-3.5 py-1.5 rounded-full text-xs font-medium">
        <span className="w-2 h-2 rounded-full bg-gray-300"></span>
        <span>Pemilihan sedang berlangsung</span>
      </div>
    </header>
  );
};