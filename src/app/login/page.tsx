// src/app/login/page.tsx
'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Header } from '@/components/layout/Header';

export default function LoginPage() {
  const router = useRouter();
  const [nim, setNim] = useState('');
  const [token, setToken] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    // Simulasi autentikasi & navigasi ke Tahap 3 (Daftar Kandidat)
    setTimeout(() => {
      setIsLoading(false);
      router.push('/voter/candidates');
    }, 1000);
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col justify-between font-sans">
      {/* Header Tahap 2 dari 9 */}
      <Header currentStep={2} totalSteps={9} />

      {/* Main Container */}
      <main className="flex-1 max-w-6xl w-full mx-auto px-4 md:px-8 py-8 md:py-12 flex flex-col md:flex-row items-stretch justify-center gap-0 md:gap-8 my-auto">
        
        {/* Banner Informasi Sisi Kiri (Desktop) */}
        <div className="hidden md:flex flex-1 bg-blue-600 rounded-3xl p-10 text-white flex-col justify-between shadow-xl">
          <div className="space-y-6">
            <div className="w-12 h-12 bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl flex items-center justify-center text-2xl">
              🛡️
            </div>

            <h1 className="text-3xl lg:text-4xl font-bold leading-tight">
              Satu identitas. <br />
              Satu suara. <br />
              Satu pilihan bermakna.
            </h1>

            <p className="text-sm text-blue-100 max-w-md leading-relaxed">
              Sistem memastikan hanya pemilih terdaftar yang dapat mengakses surat suara, tanpa menyimpan hubungan antara identitas dan pilihan.
            </p>

            <div className="space-y-3 pt-4 text-xs font-medium text-blue-50">
              <div className="flex items-center gap-2.5">
                <span className="w-5 h-5 rounded-full bg-blue-500/60 border border-blue-400 flex items-center justify-center text-[10px]">✓</span>
                <span>Token unik sekali pakai</span>
              </div>
              <div className="flex items-center gap-2.5">
                <span className="w-5 h-5 rounded-full bg-blue-500/60 border border-blue-400 flex items-center justify-center text-[10px]">✓</span>
                <span>Verifikasi identitas berlapis</span>
              </div>
              <div className="flex items-center gap-2.5">
                <span className="w-5 h-5 rounded-full bg-blue-500/60 border border-blue-400 flex items-center justify-center text-[10px]">✓</span>
                <span>Data suara terenkripsi</span>
              </div>
            </div>
          </div>

          <p className="text-[11px] text-blue-200/80 pt-8">
            Ada kendala akses? Hubungi Posko Panitia Pemilihan di Gedung Kemahasiswaan lantai 1.
          </p>
        </div>

        {/* Form Login Sisi Kanan */}
        <div className="w-full md:w-[440px] bg-white border border-gray-100 rounded-3xl p-6 md:p-10 shadow-xl shadow-slate-200/50 flex flex-col justify-between my-auto">
          <div className="space-y-6">
            <div>
              <span className="text-[11px] font-bold tracking-wider text-blue-600 uppercase">Akses Pemilih</span>
              <h2 className="text-2xl font-extrabold text-gray-900 mt-1">Masuk ke ruang pemilihan</h2>
              <p className="text-xs text-gray-500 mt-1">Masukkan identitas mahasiswa dan token pribadi Anda.</p>
            </div>

            <form onSubmit={handleLogin} className="space-y-4">
              {/* Input NIM */}
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-gray-700">Nomor Induk Mahasiswa (NIM)</label>
                <div className="relative">
                  <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400 text-sm">🪪</span>
                  <input
                    type="text"
                    required
                    placeholder="Contoh: 2310112345"
                    value={nim}
                    onChange={(e) => setNim(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 bg-gray-50/50 border border-gray-200 rounded-2xl text-xs text-gray-900 focus:outline-none focus:border-blue-600 focus:bg-white transition-all"
                  />
                </div>
                <p className="text-[10px] text-gray-400">Gunakan NIM aktif yang terdaftar pada semester ini.</p>
              </div>

              {/* Input Token */}
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-gray-700">Token pemilihan</label>
                <div className="relative">
                  <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400 text-sm">🔑</span>
                  <input
                    type="password"
                    required
                    placeholder="Masukkan 8 digit token"
                    value={token}
                    onChange={(e) => setToken(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 bg-gray-50/50 border border-gray-200 rounded-2xl text-xs text-gray-900 focus:outline-none focus:border-blue-600 focus:bg-white transition-all"
                  />
                </div>
                <p className="text-[10px] text-gray-400">Token bersifat rahasia dan hanya dapat digunakan satu kali.</p>
              </div>

              {/* Tombol Masuk */}
              <button
                type="submit"
                disabled={isLoading}
                className="w-full py-3.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-2xl flex items-center justify-center gap-2 transition-all shadow-md shadow-blue-500/20 text-sm mt-2 disabled:bg-blue-400"
              >
                <span>{isLoading ? 'Memproses...' : 'Masuk'}</span>
                <span>➔</span>
              </button>
            </form>

            <p className="text-[11px] text-gray-400 text-center flex items-center justify-center gap-1">
              <span>🔒</span> Suara Anda terenkripsi dan hanya dapat diberikan satu kali.
            </p>
          </div>

          <div className="mt-6 pt-4 border-t border-gray-100 text-center">
            <p className="text-[11px] text-gray-400">
              Panitia Pemira HMTD • <a href="mailto:pemira@kampus.ac.id" className="underline hover:text-blue-600">pemira@kampus.ac.id</a>
            </p>
          </div>
        </div>

      </main>

      {/* Footer */}
      <footer className="w-full py-4 text-center text-xs text-gray-400 border-t border-gray-100">
        © 2026 Populi — Sistem Pemilihan Umum Kampus Digital
      </footer>
    </div>
  );
}