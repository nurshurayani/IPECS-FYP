import React, { useState, useRef, useEffect } from 'react';
import { Camera, Upload, AlertCircle, FileText, Check, CheckCircle } from 'lucide-react';
import { RECEIPT_PRESETS } from '../../data';
import { Transaction, TranslationSet, Category } from '../../types';

interface ReceiptEntryPageProps {
  onAddTransaction: (tx: Omit<Transaction, 'id'>) => void;
  t: TranslationSet;
}

export default function ReceiptEntryPage({ onAddTransaction, t }: ReceiptEntryPageProps) {
  const [activeTab, setActiveTab] = useState<'ocr' | 'manual'>('ocr');
  
  // OCR Tab States
  const [isExtracting, setIsExtracting] = useState(false);
  const [extractedData, setExtractedData] = useState<typeof RECEIPT_PRESETS[0] & { date: string } | null>(null);
  const [confidence, setConfidence] = useState<number>(100);
  const [ocrMerchant, setOcrMerchant] = useState('');
  const [ocrAmount, setOcrAmount] = useState<number>(0);
  const [ocrDate, setOcrDate] = useState('');
  const [ocrCategory, setOcrCategory] = useState<Category>('Food & Dining');
  const [ocrNotes, setOcrNotes] = useState('');
  
  // Camera Simulation States
  const [showCamera, setShowCamera] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);
  const [cameraError, setCameraError] = useState<string | null>(null);

  // Manual Tab States
  const [manualMerchant, setManualMerchant] = useState('');
  const [manualAmount, setManualAmount] = useState<number>(0);
  const [manualDate, setManualDate] = useState(new Date().toISOString().substring(0, 10));
  const [manualCategory, setManualCategory] = useState<Category>('Food & Dining');
  const [manualNotes, setManualNotes] = useState('');

  // Status/Toast Alert
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const categories: Category[] = [
    'Food & Dining',
    'Transport',
    'Shopping',
    'Bills',
    'Entertainment',
    'Other'
  ];

  // OCR Simulator engine
  const triggerOCRExtraction = () => {
    setIsExtracting(true);
    setExtractedData(null);
    setSuccessMessage(null);

    setTimeout(() => {
      // Pick a random preset
      const preset = RECEIPT_PRESETS[Math.floor(Math.random() * RECEIPT_PRESETS.length)];
      
      // Assign fake relevant dates (during June 2025)
      const days = ['12', '14', '15', '16', '17', '18'];
      const randomDay = days[Math.floor(Math.random() * days.length)];
      const dateStr = `2025-06-${randomDay}`;

      setExtractedData({
        ...preset,
        date: dateStr
      });
      setConfidence(preset.confidence);
      setOcrMerchant(preset.merchant);
      setOcrAmount(preset.amount);
      setOcrDate(dateStr);
      setOcrCategory(preset.category as Category);
      setOcrNotes('OCR Scanned Receipt');
      setIsExtracting(false);
    }, 2000); // 2 seconds spinner to feel realistic
  };

  // Handle Drag & Drop / File Select
  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      triggerOCRExtraction();
    }
  };

  // Start Real Camera Capturing if permitted
  const startCamera = async () => {
    setShowCamera(true);
    setCameraError(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
    } catch (err: any) {
      console.warn("Camera access denied or unavailable", err);
      setCameraError("Camera access or preview not supported in system sandbox. Simulating image scan...");
    }
  };

  const stopCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      stream.getTracks().forEach(track => track.stop());
    }
    setShowCamera(false);
  };

  const capturePhoto = () => {
    stopCamera();
    triggerOCRExtraction();
  };

  useEffect(() => {
    return () => {
      // Cleanup camera streams if any
      if (videoRef.current && videoRef.current.srcObject) {
        const stream = videoRef.current.srcObject as MediaStream;
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  // Save manual transaction
  const handleSaveManual = (e: React.FormEvent) => {
    e.preventDefault();
    if (!manualMerchant || manualAmount <= 0) return;

    onAddTransaction({
      merchant: manualMerchant,
      amount: manualAmount,
      date: manualDate,
      category: manualCategory,
      notes: manualNotes,
      source: 'manual'
    });

    const msg = t.successAdded
      .replace('{amount}', manualAmount.toFixed(2))
      .replace('{category}', manualCategory);

    setSuccessMessage(msg);
    // Reset Form
    setManualMerchant('');
    setManualAmount(0);
    setManualNotes('');

    setTimeout(() => setSuccessMessage(null), 4000);
  };

  // Save OCR transaction
  const handleSaveOCR = () => {
    if (!ocrMerchant || ocrAmount <= 0) return;

    onAddTransaction({
      merchant: ocrMerchant,
      amount: ocrAmount,
      date: ocrDate,
      category: ocrCategory,
      notes: ocrNotes,
      source: 'ocr'
    });

    const msg = t.successAdded
      .replace('{amount}', ocrAmount.toFixed(2))
      .replace('{category}', ocrCategory);

    setSuccessMessage(msg);
    setExtractedData(null); // Clear OCR panel

    setTimeout(() => setSuccessMessage(null), 4000);
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Title */}
      <div className="border-b border-[#e0f1ee] pb-4">
        <h2 className="text-2xl font-bold text-gray-800 font-sans tracking-tight">
          {t.receiptEntry.replace(/^[^\w\s]+/g, '').trim()}
        </h2>
        <p className="text-sm text-gray-500 font-mono">
          Upload Mamak / RapidKL receipts or enter data manually.
        </p>
      </div>

      {/* Success Notification Alert */}
      {successMessage && (
        <div className="bg-[#f0fdfa] border-2 border-[#10B981] rounded-xl p-4 flex items-center gap-3 animate-bounce">
          <CheckCircle className="h-6 w-6 text-[#10B981] shrink-0" />
          <p className="text-sm font-semibold text-gray-800 leading-normal">{successMessage}</p>
        </div>
      )}

      {/* Navigation tabs mimicking Streamlit's UI */}
      <div className="flex border-b border-gray-200">
        <button
          onClick={() => { setActiveTab('ocr'); setSuccessMessage(null); }}
          className={`flex-1 py-3 text-center border-b-2 font-medium text-sm transition-all duration-150 ${
            activeTab === 'ocr'
              ? 'border-[#0F7B6C] text-[#0F7B6C]'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-200'
          }`}
        >
          {t.ocrTab}
        </button>
        <button
          onClick={() => { setActiveTab('manual'); setSuccessMessage(null); }}
          className={`flex-1 py-3 text-center border-b-2 font-medium text-sm transition-all duration-150 ${
            activeTab === 'manual'
              ? 'border-[#0F7B6C] text-[#0F7B6C]'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-200'
          }`}
        >
          {t.manualTab}
        </button>
      </div>

      {/* OCR Receipt Upload Tab */}
      {activeTab === 'ocr' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            
            {/* Upload Zone */}
            <div className="bg-white border-2 border-dashed border-[#b4e2da] hover:border-[#0F7B6C] rounded-xl p-8 flex flex-col items-center justify-center text-center transition-all cursor-pointer relative group">
              <input
                type="file"
                accept="image/*"
                onChange={handleFileUpload}
                className="absolute inset-0 opacity-0 cursor-pointer"
              />
              <div className="w-12 h-12 rounded-full bg-[#0F7B6C]/10 text-[#0F7B6C] flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <Upload className="h-6 w-6" />
              </div>
              <h4 className="text-sm font-bold text-gray-800 mb-1">{t.uploadReceiptLabel}</h4>
              <p className="text-xs text-gray-400 font-mono">JPG, PNG up to 10MB</p>
            </div>

            {/* Camera Zone */}
            <div className="bg-white border-2 border-dashed border-[#b4e2da] hover:border-[#0F7B6C] rounded-xl p-8 flex flex-col items-center justify-center text-center transition-all">
              {!showCamera ? (
                <>
                  <div className="w-12 h-12 rounded-full bg-[#0F7B6C]/10 text-[#0F7B6C] flex items-center justify-center mb-4 cursor-pointer hover:scale-110 transition-transform" onClick={startCamera}>
                    <Camera className="h-6 w-6" />
                  </div>
                  <h4 className="text-sm font-bold text-gray-800 mb-1">{t.cameraInputLabel}</h4>
                  <button
                    onClick={startCamera}
                    className="mt-2 text-xs font-mono font-bold text-[#0F7B6C] bg-[#0F7B6C]/10 px-3 py-1.5 rounded-lg hover:bg-[#0F7B6C]/20 transition-all"
                  >
                    🚀 ACTIVATE CAMERA
                  </button>
                </>
              ) : (
                <div className="w-full space-y-3">
                  <div className="relative aspect-video bg-black rounded-lg overflow-hidden flex items-center justify-center">
                    {cameraError ? (
                      <div className="p-4 text-center">
                        <AlertCircle className="h-8 w-8 text-amber-500 mx-auto mb-2" />
                        <p className="text-xs text-gray-400 font-mono mb-2">{cameraError}</p>
                        <button
                          onClick={capturePhoto}
                          className="px-3 py-1.5 bg-[#0F7B6C] text-white rounded text-xs px-4 font-bold"
                        >
                          Simulate Capture
                        </button>
                      </div>
                    ) : (
                      <video ref={videoRef} autoPlay playsInline className="w-full h-full object-cover" />
                    )}
                  </div>
                  <div className="flex gap-2 justify-center">
                    <button
                      onClick={capturePhoto}
                      className="px-4 py-2 bg-[#0F7B6C] hover:bg-[#0a5c51] text-white text-xs font-bold rounded-lg transition-all"
                    >
                      📸 SHUTTER SPEED CAPTURE
                    </button>
                    <button
                      onClick={stopCamera}
                      className="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 text-xs font-bold rounded-lg transition-all"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Spinner Loader when triggering OCR */}
          {isExtracting && (
            <div className="bg-white border border-[#e0f1ee] rounded-xl p-8 flex flex-col items-center justify-center text-center shadow-sm">
              <div className="relative w-12 h-12 flex items-center justify-center">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#0F7B6C]/30 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-8 w-8 bg-[#0F7B6C] flex items-center justify-center text-white text-xs font-bold font-mono">AI</span>
              </div>
              <h4 className="text-sm font-bold text-gray-700 mt-4">{t.extractingSpinner}</h4>
              <p className="text-xs text-gray-400 mt-1 font-mono">Running Gemini 3.5 Models for high OCR precision...</p>
            </div>
          )}

          {/* OCR Result card */}
          {extractedData && (
            <div className="bg-white border-2 border-[#0F7B6C] rounded-xl p-6 shadow-md animate-fade-in space-y-4">
              <div className="flex items-center justify-between border-b border-gray-100 pb-3">
                <div className="flex items-center gap-2">
                  <div className="bg-[#0F7B6C] text-white p-1 rounded-md">
                    <FileText className="h-4 w-4" />
                  </div>
                  <h3 className="text-sm font-bold text-gray-800">{t.ocrResult}</h3>
                </div>
                <span className="text-xs font-mono font-semibold bg-green-50 text-green-600 border border-green-100 px-2 py-0.5 rounded-full">
                  🎯 confidence: {confidence}%
                </span>
              </div>

              {/* Grid content editable form fields */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="text-xs font-mono text-gray-500 font-bold block mb-1 uppercase">
                    {t.merchantName}
                  </label>
                  <input
                    type="text"
                    value={ocrMerchant}
                    onChange={(e) => setOcrMerchant(e.target.value)}
                    className="w-full text-sm rounded-lg border border-[#cbd5e1] p-2.5 focus:border-[#0F7B6C] focus:ring-1 focus:ring-[#0F7B6C]"
                  />
                </div>

                <div>
                  <label className="text-xs font-mono text-gray-500 font-bold block mb-1 uppercase">
                    {t.amountLabel}
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    min="0.01"
                    value={ocrAmount}
                    onChange={(e) => setOcrAmount(parseFloat(e.target.value) || 0)}
                    className="w-full text-sm rounded-lg border border-[#cbd5e1] p-2.5 focus:border-[#0F7B6C] focus:ring-1 focus:ring-[#0F7B6C]"
                  />
                </div>

                <div>
                  <label className="text-xs font-mono text-gray-500 font-bold block mb-1 uppercase">
                    {t.dateLabel}
                  </label>
                  <input
                    type="date"
                    value={ocrDate}
                    onChange={(e) => setOcrDate(e.target.value)}
                    className="w-full text-sm rounded-lg border border-[#cbd5e1] p-2.5 focus:border-[#0F7B6C] focus:ring-1 focus:ring-[#0F7B6C] font-mono"
                  />
                </div>

                <div>
                  <label className="text-xs font-mono text-gray-500 font-bold block mb-1 uppercase">
                    {t.categoryLabel}
                  </label>
                  <select
                    value={ocrCategory}
                    onChange={(e) => setOcrCategory(e.target.value as Category)}
                    className="w-full text-sm rounded-lg border border-[#cbd5e1] p-2.5 focus:border-[#0F7B6C] focus:ring-1 focus:ring-[#0F7B6C]"
                  >
                    {categories.map((c) => (
                      <option key={c} value={c}>
                        {c}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="md:col-span-2">
                  <label className="text-xs font-mono text-gray-500 font-bold block mb-1 uppercase">
                    {t.notesLabel}
                  </label>
                  <textarea
                    rows={2}
                    value={ocrNotes}
                    onChange={(e) => setOcrNotes(e.target.value)}
                    className="w-full text-sm rounded-lg border border-[#cbd5e1] p-2.5 focus:border-[#0F7B6C] focus:ring-1 focus:ring-[#0F7B6C]"
                  />
                </div>
              </div>

              {/* Confirm submit trigger button */}
              <button
                onClick={handleSaveOCR}
                className="w-full bg-[#0F7B6C] hover:bg-[#0a5c51] text-white py-3 px-4 rounded-lg font-bold text-sm transition-all shadow-md hover:shadow-lg flex items-center justify-center gap-2"
              >
                <Check className="h-5 w-5" />
                <span>{t.confirmSave}</span>
              </button>
            </div>
          )}
        </div>
      )}

      {/* Manual Data Form Tab */}
      {activeTab === 'manual' && (
        <form onSubmit={handleSaveManual} className="bg-white border border-[#e0f1ee] rounded-xl p-6 shadow-sm space-y-4">
          <div>
            <label className="text-xs font-mono text-gray-500 font-bold block mb-1 uppercase">
              {t.merchantName} <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              required
              placeholder="e.g. Restoran Ali Maju Mamak"
              value={manualMerchant}
              onChange={(e) => setManualMerchant(e.target.value)}
              className="w-full text-sm rounded-lg border border-[#cbd5e1] p-2.5 focus:border-[#0F7B6C] focus:ring-1 focus:ring-[#0F7B6C]"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="text-xs font-mono text-gray-500 font-bold block mb-1 uppercase">
                {t.amountLabel} <span className="text-red-500">*</span>
              </label>
              <input
                type="number"
                step="0.01"
                min="0.01"
                required
                value={manualAmount || ''}
                onChange={(e) => setManualAmount(parseFloat(e.target.value) || 0)}
                className="w-full text-sm rounded-lg border border-[#cbd5e1] p-2.5 focus:border-[#0F7B6C] focus:ring-1 focus:ring-[#0F7B6C] font-mono"
              />
            </div>

            <div>
              <label className="text-xs font-mono text-gray-500 font-bold block mb-1 uppercase">
                {t.dateLabel} <span className="text-red-500">*</span>
              </label>
              <input
                type="date"
                required
                value={manualDate}
                onChange={(e) => setManualDate(e.target.value)}
                className="w-full text-sm rounded-lg border border-[#cbd5e1] p-2.5 focus:border-[#0F7B6C] focus:ring-1 focus:ring-[#0F7B6C] font-mono"
              />
            </div>

            <div>
              <label className="text-xs font-mono text-gray-500 font-bold block mb-1 uppercase">
                {t.categoryLabel} <span className="text-red-500">*</span>
              </label>
              <select
                value={manualCategory}
                onChange={(e) => setManualCategory(e.target.value as Category)}
                className="w-full text-sm rounded-lg border border-[#cbd5e1] p-2.5 focus:border-[#0F7B6C] focus:ring-1 focus:ring-[#0F7B6C]"
              >
                {categories.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="text-xs font-mono text-gray-500 font-bold block mb-1 uppercase">
              {t.notesLabel}
            </label>
            <textarea
              rows={3}
              placeholder="e.g. Gather with club members"
              value={manualNotes}
              onChange={(e) => setManualNotes(e.target.value)}
              className="w-full text-sm rounded-lg border border-[#cbd5e1] p-2.5 focus:border-[#0F7B6C] focus:ring-1 focus:ring-[#0F7B6C]"
            />
          </div>

          <button
            type="submit"
            className="w-full bg-[#0F7B6C] hover:bg-[#0a5c51] text-white py-3 px-4 rounded-lg font-bold text-sm transition-all shadow-md hover:shadow-lg flex items-center justify-center gap-2"
          >
            <CheckCircle className="h-5 w-5" />
            <span>{t.saveTransaction}</span>
          </button>
        </form>
      )}
    </div>
  );
}
