'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function LoginPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({ name: '', nim: '' });
  const [error, setError] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name.trim() || !formData.nim.trim()) {
      setError('Silakan isi Nama Lengkap dan NIM Anda');
      return;
    }
    // Lanjut ke alur verifikasi berikutnya (misal verifikasi wajah / token)
    router.push('/voter/verify');
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] bg-[#121212] text-white flex flex-col justify-between font-sans">
      <main className="flex-1 w-full max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-2 min-h-[calc(100vh-4rem)]">
        
        {/* Sisi Kiri: Deskripsi & Informasi Keamanan */}
        <div className="p-8 md:p-16 flex flex-col justify-center space-y-8 bg-[#18181b]/50 border-r border-[#27272a]">
          <div className="w-10 h-10 rounded-xl bg-[#27272a] border border-[#3f3f46] flex items-center justify-center text-gray-300">
            🛡️
          </div>

          <h1 className="text-3xl md:text-5xl font-extrabold text-white leading-tight">
            Satu identitas. Satu suara. Satu pilihan bermakna.
          </h1>

          <p className="text-sm md:text-base text-gray-400 leading-relaxed max-w-lg">
            Sistem memastikan hanya pemilih terdaftar yang dapat mengakses surat suara, tanpa menyimpan hubungan antara identitas dan pilihan.
          </p>

          <div className="space-y-4 pt-2 text-sm text-gray-300">
            <div className="flex items-center gap-3">
              <span className="text-emerald-400">✓</span>
              <span>Token unik sekali pakai</span>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-emerald-400">✓</span>
              <span>Verifikasi identitas berlapis</span>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-emerald-400">✓</span>
              <span>Data suara terenkripsi</span>
            </div>
          </div>

          <div className="pt-8 text-xs text-gray-400 max-w-md border-t border-[#27272a]">
            Ada kendala akses? Hubungi Posko Panitia Pemilihan di Gedung Kemahasiswaan lantai 1.
          </div>
        </div>

        {/* Sisi Kanan: Form Akses Pemilih */}
        <div className="p-8 md:p-16 flex flex-col justify-center items-center">
          <div className="w-full max-w-md bg-[#18181b] border border-[#27272a] rounded-3xl p-6 md:p-8 shadow-2xl space-y-6">
            <div>
              <p className="text-[11px] font-bold text-gray-400 uppercase tracking-wider">Akses Pemilih</p>
              <h2 className="text-2xl font-bold text-white mt-1">Masuk ke ruang pemilihan</h2>
              <p className="text-xs text-gray-400 mt-1">
                Masukkan identitas mahasiswa dan token pribadi Anda.
              </p>
            </div>

            {error && (
              <div className="p-3 bg-red-950/50 border border-red-800 rounded-xl text-xs text-red-300">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-5">
              <div className="space-y-1.5">
                <label className="text-xs font-medium text-gray-300">Nama</label>
                <div className="relative">
                  <span className="absolute left-3.5 top-3 text-gray-400 text-sm">🪪</span>
                  <input
                    type="text"
                    placeholder="Masukkan nama lengkap"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="w-full pl-10 pr-4 py-2.5 bg-[#09090b] border border-[#27272a] rounded-xl text-sm text-white placeholder-gray-500 focus:outline-none focus:border-gray-400 transition-colors"
                  />
                </div>
                <p className="text-[11px] text-gray-400">Gunakan nama lengkap sesuai data mahasiswa.</p>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-medium text-gray-300">NIM</label>
                <div className="relative">
                  <span className="absolute left-3.5 top-3 text-gray-400 text-sm">🔑</span>
                  <input
                    type="text"
                    placeholder="Masukkan NIM"
                    value={formData.nim}
                    onChange={(e) => setFormData({ ...formData, nim: e.target.value })}
                    className="w-full pl-10 pr-4 py-2.5 bg-[#09090b] border border-[#27272a] rounded-xl text-sm text-white placeholder-gray-500 focus:outline-none focus:border-gray-400 transition-colors"
                  />
                </div>
                <p className="text-[11px] text-gray-400">Gunakan NIM aktif yang terdaftar pada semester ini.</p>
              </div>

              <button
                type="submit"
                className="w-full py-3 bg-gray-200 hover:bg-white text-gray-900 font-semibold rounded-2xl flex items-center justify-center gap-2 transition-all text-sm mt-4"
              >
                <span>Next</span>
                <span>➔</span>
              </button>
            </form>

            <p className="text-[11px] text-gray-400 text-center flex items-center justify-center gap-1.5 pt-2">
              <span>🔒</span> Suara Anda terenkripsi dan hanya dapat diberikan satu kali.
            </p>
          </div>

          <p className="text-xs text-gray-400 mt-6 text-center">
            Panitia Pemira HMTD • pemira@kampus.ac.id
          </p>
        </div>

      </main>
    </div>
  );
}