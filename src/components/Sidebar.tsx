import { LayoutDashboard, FileText, ListOrdered, Target, BarChart3, Brain, Languages } from 'lucide-react';
import { TranslationSet } from '../types';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  lang: 'en' | 'bm';
  setLang: (lang: 'en' | 'bm') => void;
  t: TranslationSet;
}

export default function Sidebar({ activeTab, setActiveTab, lang, setLang, t }: SidebarProps) {
  const menuItems = [
    { id: 'dashboard', label: t.dashboard, icon: LayoutDashboard },
    { id: 'receipt_entry', label: t.receiptEntry, icon: FileText },
    { id: 'transactions', label: t.transactions, icon: ListOrdered },
    { id: 'budget', label: t.budgets, icon: Target },
    { id: 'reports', label: t.reports, icon: BarChart3 },
    { id: 'forecast_alerts', label: t.forecastAlerts, icon: Brain },
  ];

  return (
    <aside className="w-80 bg-[#f8fffe] border-r border-[#e0f1ee] h-screen flex flex-col fixed left-0 top-0 text-[#213547]">
      {/* Brand logo/name */}
      <div className="p-6 border-b border-[#e0f1ee]">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-3xl" role="img" aria-label="card">💳</span>
          <h1 className="text-2xl font-bold font-sans tracking-tight text-[#0F7B6C]">IPECS</h1>
        </div>
        <p className="text-xs font-mono text-[#0a5c51]/70 tracking-wider uppercase">{t.logoSubtitle}</p>
      </div>

      {/* User Info Card */}
      <div className="p-4 mx-4 mt-4 bg-white rounded-xl border border-[#e0f1ee] shadow-sm">
        <p className="text-xs font-mono font-bold text-[#0F7B6C] mb-1">CURRENT USER</p>
        <p className="text-sm font-semibold text-gray-800">{t.userId.split('—')[0].trim()}</p>
        <p className="text-xs text-gray-500 mt-0.5">{t.userId.split('—')[1]?.trim() || t.userId}</p>
      </div>

      {/* Navigation menu */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              id={`sidebar-item-${item.id}`}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200 ${
                isActive
                  ? 'bg-[#0F7B6C] text-white shadow-md shadow-[#0F7B6C]/20'
                  : 'hover:bg-[#0F7B6C]/10 text-gray-700 hover:text-[#0F7B6C]'
              }`}
            >
              <Icon className={`h-5 w-5 ${isActive ? 'text-white' : 'text-gray-500'}`} />
              <span className="translate-y-[-0.5px] truncate">{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* EN/BM toggle at bottom */}
      <div className="p-4 border-t border-[#e0f1ee] bg-white">
        <div className="flex items-center justify-between px-2">
          <div className="flex items-center gap-2">
            <Languages className="h-4 w-4 text-[#0F7B6C]" />
            <span className="text-xs font-mono font-medium text-gray-500">BM/EN LANG</span>
          </div>
          <button
            id="lang-toggle-btn"
            onClick={() => setLang(lang === 'en' ? 'bm' : 'en')}
            className="relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none"
            style={{ backgroundColor: lang === 'bm' ? '#0F7B6C' : '#d1d5db' }}
          >
            <span
              className="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out"
              style={{ transform: lang === 'bm' ? 'translateX(20px)' : 'translateX(0px)' }}
            />
          </button>
        </div>
        <div className="text-center mt-2">
          <span className="text-[10px] font-mono text-gray-400">
            {lang === 'en' ? 'Active: English' : 'Aktif: Bahasa Malaysia'}
          </span>
        </div>
      </div>
    </aside>
  );
}
