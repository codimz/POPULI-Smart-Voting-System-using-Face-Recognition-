'use client';

import Link from 'next/link';

export default function LandingPage() {
  return (
    <div className="bg-slate-50/50 min-h-[calc(100vh-4rem)] flex flex-col justify-between font-sans">
      {/* Main Content Area */}
      <main className="flex-1 max-w-6xl w-full mx-auto px-4 md:px-8 py-8 md:py-16 flex flex-col md:flex-row items-center justify-between gap-10">
        
        {/* Sisi Kiri: Judul & Informasi */}
        <div className="flex-1 space-y-6 text-left">
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-blue-50 border border-blue-100 rounded-full text-blue-600 text-xs font-medium">
            <span>✓ Portal resmi pemilihan mahasiswa</span>
          </div>

          <h1 className="text-3xl md:text-5xl font-extrabold text-gray-900 leading-tight">
            Pemilihan Ketua Himpunan <br />
            <span className="text-blue-600">Mahasiswa Teknologi Digital</span>
          </h1>

          <p className="text-sm md:text-base text-blue-600 font-semibold">
            Periode kepengurusan 2026/2027
          </p>

          <p className="text-sm text-gray-500 max-w-lg leading-relaxed">
            Gunakan hak suara Anda untuk memilih pemimpin yang akan membawa aspirasi dan kemajuan bagi seluruh mahasiswa.
          </p>

          <div className="flex items-center gap-6 text-xs text-gray-600 font-medium pt-2">
            <span className="flex items-center gap-1.5">
              <span className="w-4 h-4 rounded-full border border-emerald-500 flex items-center justify-center text-[10px] text-emerald-600 font-bold">✓</span> Aman
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-4 h-4 rounded-full border border-emerald-500 flex items-center justify-center text-[10px] text-emerald-600 font-bold">✓</span> Rahasia
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-4 h-4 rounded-full border border-emerald-500 flex items-center justify-center text-[10px] text-emerald-600 font-bold">✓</span> Terverifikasi
            </span>
          </div>
        </div>

        {/* Sisi Kanan: Card Jadwal & Tombol Masuk */}
        <div className="w-full md:w-[400px] bg-white border border-gray-100 rounded-3xl p-6 md:p-8 shadow-xl shadow-slate-200/50 space-y-6">
          <div className="flex items-center gap-2 text-emerald-600 text-xs font-bold">
            <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
            Pemungutan suara dibuka
          </div>

          <div className="space-y-4 text-xs text-gray-600">
            <div className="flex items-start gap-3">
              <span className="text-base">📅</span>
              <div>
                <p className="text-gray-400">Jadwal</p>
                <p className="font-bold text-gray-800 text-sm">12–14 Oktober 2026</p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <span className="text-base">⏰</span>
              <div>
                <p className="text-gray-400">Waktu</p>
                <p className="font-bold text-gray-800 text-sm">08.00–20.00 WIB</p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <span className="text-base">👥</span>
              <div>
                <p className="text-gray-400">Pemilih</p>
                <p className="font-bold text-gray-800 text-sm">Mahasiswa aktif 2026</p>
              </div>
            </div>
          </div>

          <div className="bg-blue-50/60 border border-blue-100/80 rounded-2xl p-3.5 text-[11px] text-blue-700 leading-relaxed flex items-start gap-2">
            <span>ℹ️</span>
            <span>Siapkan NIM dan token yang dikirimkan melalui email institusi.</span>
          </div>

          {/* Tombol ke Halaman Login */}
          <Link
            href="/login"
            className="w-full py-3.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-2xl flex items-center justify-center gap-2 transition-all shadow-md shadow-blue-500/20 text-sm"
          >
            <span>Masuk untuk memilih</span>
            <span>➔</span>
          </Link>

          <p className="text-[11px] text-gray-400 text-center flex items-center justify-center gap-1">
            <span>🔒</span> Suara Anda terenkripsi dan hanya dapat diberikan satu kali.
          </p>
        </div>

      </main>

      {/* Footer */}
      <footer className="w-full py-4 text-center text-xs text-gray-400 border-t border-gray-100">
        © 2026 Populi — Sistem Pemilihan Umum Kampus Digital
      </footer>
    </div>
  );
}