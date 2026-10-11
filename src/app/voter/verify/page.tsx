// src/app/voter/verify/page.tsx
'use client';

import React, { useState, useRef, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import Webcam from 'react-webcam';
import { Header } from '@/components/layout/Header';

export default function VerifyPage() {
  const router = useRouter();
  const webcamRef = useRef<Webcam>(null);
  const [capturedImage, setCapturedImage] = useState<string | null>(null);
  const [isVerifying, setIsVerifying] = useState(false);

  // Ambil foto dari kamera webcam
  const capture = useCallback(() => {
    if (webcamRef.current) {
      const imageSrc = webcamRef.current.getScreenshot();
      setCapturedImage(imageSrc);
    }
  }, [webcamRef]);

  // Ulangi foto jika kurang jelas
  const handleRetake = () => {
    setCapturedImage(null);
  };

  // Konfirmasi dan kirim data verifikasi ke halaman bukti suara (Receipt)
  const handleConfirmVote = () => {
    setIsVerifying(true);

    // Simulasi proses pengiriman & enkripsi suara
    setTimeout(() => {
      setIsVerifying(false);
      router.push('/voter/success');
    }, 1500);
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col justify-between font-sans pb-12">
      {/* Header Tahap 4 dari 9 */}
      <Header currentStep={4} totalSteps={9} />

      <main className="flex-1 max-w-4xl w-full mx-auto px-4 md:px-8 py-8 space-y-8">
        
        {/* Banner Penjelasan */}
        <div className="bg-white border border-gray-100 rounded-3xl p-6 md:p-8 shadow-sm text-center space-y-2">
          <span className="text-[11px] font-bold tracking-wider text-blue-600 uppercase">Verifikasi Kehadiran Pemilih</span>
          <h1 className="text-2xl md:text-3xl font-extrabold text-gray-900">
            Pemindaian Wajah (Biometrik)
          </h1>
          <p className="text-xs md:text-sm text-gray-500 max-w-md mx-auto leading-relaxed">
            Posisikan wajah Anda di dalam bingkai untuk memastikan keabsahan pemilih sebelum suara Anda disimpan.
          </p>
        </div>

        {/* Box Kamera / Tampilan Hasil Tangkapan */}
        <div className="bg-white border border-gray-100 rounded-3xl p-6 md:p-8 shadow-xl max-w-lg mx-auto space-y-6">
          <div className="relative w-full aspect-video bg-slate-900 rounded-2xl overflow-hidden shadow-inner flex items-center justify-center border-2 border-dashed border-blue-200">
            {!capturedImage ? (
              <>
                <Webcam
                  audio={false}
                  ref={webcamRef}
                  screenshotFormat="image/jpeg"
                  className="w-full h-full object-cover"
                />
                {/* Frame Bantuan Oval untuk Wajah */}
                <div className="absolute inset-0 border-4 border-blue-500/40 rounded-full scale-75 pointer-events-none animate-pulse"></div>
              </>
            ) : (
              <img
                src={capturedImage}
                alt="Wajah Terverifikasi"
                className="w-full h-full object-cover"
              />
            )}
          </div>

          {/* Control Buttons */}
          <div className="space-y-3">
            {!capturedImage ? (
              <button
                onClick={capture}
                className="w-full py-3.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-2xl transition-all shadow-md shadow-blue-500/20 text-xs flex items-center justify-center gap-2"
              >
                <span>📷</span>
                <span>Ambil Foto Verifikasi</span>
              </button>
            ) : (
              <div className="flex gap-3">
                <button
                  onClick={handleRetake}
                  disabled={isVerifying}
                  className="flex-1 py-3 bg-gray-100 hover:bg-gray-200 text-gray-700 font-semibold rounded-2xl text-xs transition-all"
                >
                  Foto Ulang
                </button>
                <button
                  onClick={handleConfirmVote}
                  disabled={isVerifying}
                  className="flex-1 py-3 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold rounded-2xl text-xs transition-all shadow-md shadow-emerald-500/20 flex items-center justify-center gap-2 disabled:bg-emerald-400"
                >
                  <span>{isVerifying ? 'Verifikasi...' : 'Konfirmasi Suara'}</span>
                  <span>➔</span>
                </button>
              </div>
            )}
          </div>

          <p className="text-[11px] text-gray-400 text-center flex items-center justify-center gap-1">
            <span>🔒</span> Foto ini hanya digunakan untuk pencocokan kehadiran dan tidak dikaitkan dengan pilihan kandidat Anda.
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