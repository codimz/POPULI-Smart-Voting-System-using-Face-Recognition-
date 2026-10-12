'use client';

import Link from 'next/link';

export default function LandingPage() {
  return (
    <div className="bg-[#121212] min-h-[calc(100vh-4rem)] text-white flex flex-col justify-between font-sans">
      {/* Main Content Area */}
      <main className="flex-1 max-w-6xl w-full mx-auto px-4 md:px-8 py-10 md:py-16 flex flex-col md:flex-row items-center justify-between gap-10">
        
        {/* Sisi Kiri: Judul & Informasi */}
        <div className="flex-1 space-y-6 text-left">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 bg-[#1f1f1f] border border-[#2e2e2e] rounded-full text-xs text-gray-300 font-medium">
            <span className="w-4 h-4 rounded-full border border-gray-400 flex items-center justify-center text-[10px]">✓</span>
            <span>Portal resmi pemilihan mahasiswa</span>
          </div>

          <h1 className="text-3xl md:text-5xl font-extrabold text-white leading-tight tracking-tight">
            Pemilihan Ketua Himpunan <br />
            Mahasiswa Teknologi Digital
          </h1>

          <p className="text-sm md:text-base text-gray-400 font-medium">
            Periode kepengurusan 2026/2027
          </p>

          <p className="text-sm text-gray-400 max-w-lg leading-relaxed">
            Gunakan hak suara Anda untuk memilih pemimpin yang akan membawa aspirasi dan kemajuan bagi seluruh mahasiswa.
          </p>

          <div className="flex items-center gap-6 text-xs text-gray-400 font-medium pt-2">
            <span className="flex items-center gap-2">
              <span className="w-4 h-4 rounded-full border border-gray-500 flex items-center justify-center text-[10px]">◯</span> Aman
            </span>
            <span className="flex items-center gap-2">
              <span className="w-4 h-4 rounded-full border border-gray-500 flex items-center justify-center text-[10px]">◯</span> Rahasia
            </span>
            <span className="flex items-center gap-2">
              <span className="w-4 h-4 rounded-full border border-gray-500 flex items-center justify-center text-[10px]">◯</span> Terverifikasi
            </span>
          </div>
        </div>

        {/* Sisi Kanan: Card Jadwal & Tombol Masuk */}
        <div className="w-full md:w-[420px] bg-[#18181b] border border-[#27272a] rounded-3xl p-6 md:p-8 shadow-2xl space-y-6">
          {/* Titik Putih/Abu-abu Netral */}
          <div className="flex items-center gap-2 text-gray-300 text-xs font-semibold">
            <span className="w-2 h-2 rounded-full bg-gray-300"></span>
            <span>Pemungutan suara dibuka</span>
          </div>

          <div className="space-y-4 text-xs text-gray-300">
            {/* Jadwal */}
            <div className="flex items-start gap-3">
              <div className="w-9 h-9 bg-[#27272a] border border-[#3f3f46]/60 rounded-xl flex items-center justify-center text-gray-300">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="0 0h24v24H0z" fill="none"/>
                  <rect x="4" y="5" width="16" height="16" rx="2" strokeWidth={1.5} />
                  <line x1="16" y1="3" x2="16" y2="7" strokeWidth={1.5} />
                  <line x1="8" y1="3" x2="8" y2="7" strokeWidth={1.5} />
                  <line x1="4" y1="11" x2="20" y2="11" strokeWidth={1.5} />
                </svg>
              </div>
              <div>
                <p className="text-gray-400 text-[11px]">Jadwal</p>
                <p className="font-bold text-white text-sm">12–14 Oktober 2026</p>
              </div>
            </div>

            {/* Waktu */}
            <div className="flex items-start gap-3">
              <div className="w-9 h-9 bg-[#27272a] border border-[#3f3f46]/60 rounded-xl flex items-center justify-center text-gray-300">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <circle cx="12" cy="12" r="9" strokeWidth={1.5} />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 7v5l3 2" />
                </svg>
              </div>
              <div>
                <p className="text-gray-400 text-[11px]">Waktu</p>
                <p className="font-bold text-white text-sm">08.00–20.00 WIB</p>
              </div>
            </div>

            {/* Pemilih */}
            <div className="flex items-start gap-3">
              <div className="w-9 h-9 bg-[#27272a] border border-[#3f3f46]/60 rounded-xl flex items-center justify-center text-gray-300">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M16 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2" />
                  <circle cx="10" cy="7" r="4" strokeWidth={1.5} />
                </svg>
              </div>
              <div>
                <p className="text-gray-400 text-[11px]">Pemilih</p>
                <p className="font-bold text-white text-sm">Mahasiswa aktif 2026</p>
              </div>
            </div>
          </div>

          {/* Box Info Abu-abu */}
          <div className="bg-[#27272a]/60 border border-[#3f3f46]/40 rounded-2xl p-3.5 text-[11px] text-gray-300 leading-relaxed flex items-start gap-2.5">
            <span className="w-4 h-4 rounded-full border border-gray-400 flex items-center justify-center text-[10px] shrink-0 mt-0.5 font-semibold">i</span>
            <span>Siapkan NIM dan token yang dikirimkan melalui email institusi.</span>
          </div>

          {/* Tombol ke Halaman Login */}
          <Link
            href="/login"
            className="w-full py-3.5 bg-gray-200 hover:bg-white text-gray-900 font-semibold rounded-2xl flex items-center justify-center gap-2 transition-all text-sm"
          >
            <span>➔] Masuk untuk memilih</span>
          </Link>

          <p className="text-[11px] text-gray-400 text-center flex items-center justify-center gap-1.5">
            <span>🔒</span> Suara Anda terenkripsi dan hanya dapat diberikan satu kali.
          </p>
        </div>

      </main>
    </div>
  );
}