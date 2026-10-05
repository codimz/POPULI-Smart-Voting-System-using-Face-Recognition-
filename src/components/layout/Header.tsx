// components/layout/Header.tsx
'use client';

import React from 'react';

interface HeaderProps {
  currentStep?: number;
  totalSteps?: number;
}

export const Header: React.FC<HeaderProps> = ({ currentStep = 1, totalSteps = 9 }) => {
  return (
    <header className="w-full bg-white border-b border-gray-100 px-4 md:px-8 py-3.5 flex justify-between items-center sticky top-0 z-50">
      {/* Brand Logo */}
      <div className="flex items-center gap-2.5">
        <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold shadow-sm">
          🏛️️
        </div>
        <div className="flex flex-col">
          <span className="font-bold text-gray-900 tracking-tight leading-none text-sm md:text-base">POPULI</span>
          <span className="text-[10px] text-gray-400 font-medium">POPULI</span>
        </div>
      </div>

      {/* Badge Status Pemilihan */}
      <div className="hidden md:flex items-center gap-2 bg-emerald-50 border border-emerald-100 text-emerald-700 px-3 py-1 rounded-full text-xs font-medium">
        <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
        Pemilihan sedang berlangsung
      </div>

      {/* Indikator Tahap */}
      <div className="flex items-center gap-1.5 text-xs text-gray-500 border border-gray-200 px-3 py-1 rounded-full bg-gray-50/50">
        <span className="text-blue-600 font-semibold">🛡️</span>
        <span>Tahap {currentStep} dari {totalSteps}</span>
      </div>
    </header>
  );
};