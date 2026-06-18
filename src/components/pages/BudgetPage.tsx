import React, { useState, useMemo } from 'react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Legend } from 'recharts';
import { Target, Sparkles, Check, AlertTriangle, Save } from 'lucide-react';
import { Transaction, Budgets, TranslationSet } from '../../types';

interface BudgetPageProps {
  transactions: Transaction[];
  budgets: Budgets;
  onUpdateBudgets: (updatedBudgets: Budgets) => void;
  t: TranslationSet;
}

export default function BudgetPage({ transactions, budgets, onUpdateBudgets, t }: BudgetPageProps) {
  const currentMonthStr = '2025-06';
  const [activeTab, setActiveTab] = useState<'current' | 'history'>('current');

  // Input states for managing budget limits (inline editing)
  const [tempBudgets, setTempBudgets] = useState<Budgets>({ ...budgets });
  const [isSaved, setIsSaved] = useState(false);

  // Math totals
  const totalBudget = useMemo(() => {
    return Object.values(budgets).reduce((sum, val) => sum + val, 0);
  }, [budgets]);

  const totalSpentThisMonth = useMemo(() => {
    return transactions
      .filter((tx) => tx.date.startsWith(currentMonthStr))
      .reduce((sum, tx) => sum + tx.amount, 0);
  }, [transactions]);

  const progressPercentage = useMemo(() => {
    return totalBudget > 0 ? (totalSpentThisMonth / totalBudget) * 100 : 0;
  }, [totalBudget, totalSpentThisMonth]);

  // Overall status
  const budgetStatus = useMemo(() => {
    if (progressPercentage >= 100) return { label: t.overBudget, color: 'text-red-600 bg-red-50 border-red-200' };
    if (progressPercentage >= 80) return { label: t.atRisk, color: 'text-amber-600 bg-amber-50 border-amber-200' };
    return { label: t.onTrack, color: 'text-green-600 bg-green-50 border-green-200' };
  }, [progressPercentage, t]);

  // Spending per category map
  const categorySpentMap = useMemo(() => {
    const map: { [cat: string]: number } = {};
    transactions
      .filter((tx) => tx.date.startsWith(currentMonthStr))
      .forEach((tx) => {
        map[tx.category] = (map[tx.category] || 0) + tx.amount;
      });
    return map;
  }, [transactions]);

  // Handle changing inputs
  const handleBudgetChange = (cat: keyof Budgets, value: number) => {
    setTempBudgets({
      ...tempBudgets,
      [cat]: value >= 0 ? value : 0,
    });
    setIsSaved(false);
  };

  // Submit/Save
  const handleSaveBudgets = (e: React.FormEvent) => {
    e.preventDefault();
    onUpdateBudgets(tempBudgets);
    setIsSaved(true);
    setTimeout(() => setIsSaved(false), 3000);
  };

  // Budget History grouped bar chart data (last 3 months: April, May, June 2025)
  const historyData = useMemo(() => {
    const cats = Object.keys(budgets);
    const months = ['Apr', 'May', 'Jun'];

    // Hardcode April and May totals to represent realistic historical progress
    const dummyApr: { [cat: string]: number } = {
      'Food & Dining': 282.40,
      'Transport': 78.00,
      'Shopping': 189.50,
      'Bills': 148.00,
      'Entertainment': 65.00,
      'Other': 12.00,
    };

    const dummyMay: { [cat: string]: number } = {
      'Food & Dining': 310.20, // Over budget May!
      'Transport': 95.00,
      'Shopping': 140.00,
      'Bills': 150.00,
      'Entertainment': 115.00, // Over budget May!
      'Other': 38.00,
    };

    return cats.map((cat) => {
      const budgetMax = budgets[cat as keyof Budgets] || 0;
      const actualJun = categorySpentMap[cat] || 0;
      const actualMay = dummyMay[cat] || 0;
      const actualApr = dummyApr[cat] || 0;

      return {
        category: cat,
        Budget: budgetMax,
        'April Actual': parseFloat(actualApr.toFixed(2)),
        'May Actual': parseFloat(actualMay.toFixed(2)),
        'June Actual': parseFloat(actualJun.toFixed(2)),
      };
    });
  }, [budgets, categorySpentMap]);

  const getEmoji = (cat: string) => {
    switch (cat) {
      case 'Food & Dining': return '🍔';
      case 'Transport': return '🚗';
      case 'Shopping': return '🛍️';
      case 'Bills': return '💵';
      case 'Entertainment': return '🎬';
      default: return '📦';
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Title */}
      <div className="border-b border-[#e0f1ee] pb-4">
        <h2 className="text-2xl font-bold text-gray-800 font-sans tracking-tight">
          {t.budgets.replace(/^[^\w\s]+/g, '').trim()}
        </h2>
        <p className="text-sm text-gray-500 font-mono">
          Monitor remaining cash targets and update category limits live.
        </p>
      </div>

      {/* Tabs Current vs History */}
      <div className="flex border-b border-gray-200">
        <button
          onClick={() => setActiveTab('current')}
          className={`flex-1 py-3 text-center border-b-2 font-medium text-sm transition-all duration-150 ${
            activeTab === 'current'
              ? 'border-[#0F7B6C] text-[#0F7B6C]'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-200'
          }`}
        >
          {t.currentMonth}
        </button>
        <button
          onClick={() => setActiveTab('history')}
          className={`flex-1 py-3 text-center border-b-2 font-medium text-sm transition-all duration-150 ${
            activeTab === 'history'
              ? 'border-[#0F7B6C] text-[#0F7B6C]'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-200'
          }`}
        >
          {t.history}
        </button>
      </div>

      {/* Current Month Tab */}
      {activeTab === 'current' && (
        <div className="space-y-6">
          {/* Top overall card with Progress Bar */}
          <div className="bg-white border border-[#e0f1ee] rounded-xl p-6 shadow-sm space-y-4">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
              <div>
                <h3 className="text-xs font-mono font-bold text-gray-400 uppercase tracking-wider mb-1">
                  OVERALL MONTHLY SPENDING VS TARGET
                </h3>
                <p className="text-lg font-bold text-gray-800">
                  Spent <span className="font-mono text-[#0F7B6C]">RM {totalSpentThisMonth.toFixed(2)}</span> of{' '}
                  <span className="font-mono text-gray-500">RM {totalBudget.toFixed(2)}</span>
                </p>
              </div>

              {/* Status Indicator */}
              <div
                className={`py-1.5 px-4 rounded-full text-xs font-bold border ${budgetStatus.color} animate-pulse`}
              >
                {budgetStatus.label}
              </div>
            </div>

            {/* Progress bar */}
            <div className="space-y-1">
              <div className="relative w-full h-4 bg-gray-100 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${
                    progressPercentage >= 100
                      ? 'bg-red-500'
                      : progressPercentage >= 80
                      ? 'bg-amber-500'
                      : 'bg-[#10B981]'
                  }`}
                  style={{ width: `${Math.min(progressPercentage, 100)}%` }}
                />
              </div>
              <div className="flex justify-between text-[11px] font-mono text-gray-400">
                <span>0% Usage</span>
                <span>{progressPercentage.toFixed(1)}% Used</span>
                <span>100% Target Limit</span>
              </div>
            </div>
          </div>

          {/* Form wrapper for per-category budgets table */}
          <form onSubmit={handleSaveBudgets} className="bg-white border border-[#e0f1ee] rounded-xl overflow-hidden shadow-sm">
            <div className="p-4 border-b border-[#e0f1ee] bg-[#f8fffe]/50 flex items-center justify-between">
              <span className="text-xs font-mono text-[#0a5c51]/80 font-bold uppercase tracking-wider flex items-center gap-1.5">
                <Target className="h-4 w-4 text-[#0F7B6C]" />
                <span>SET LIMITS PER CATEGORY</span>
              </span>
              {isSaved && (
                <span className="text-xs font-mono font-bold text-green-600 bg-green-50 px-2 py-1 rounded inline-flex items-center gap-1">
                  <Check className="h-3 w-3" /> Budgets Saved Successfully!
                </span>
              )}
            </div>

            {/* Custom Grid mimicking st.columns(5) */}
            <div className="p-5 space-y-5">
              <div className="hidden md:grid grid-cols-12 gap-4 pb-2 border-b border-gray-100 text-xs font-mono text-gray-400 font-bold">
                <div className="col-span-3">{t.categoryName}</div>
                <div className="col-span-2">{t.budgetLimit}</div>
                <div className="col-span-2">{t.amountSpent}</div>
                <div className="col-span-2">{t.remaining}</div>
                <div className="col-span-3">Usage Bar</div>
              </div>

              {Object.keys(budgets).map((cat) => {
                const category = cat as keyof Budgets;
                const limit = tempBudgets[category];
                const spent = categorySpentMap[cat] || 0;
                const remaining = limit - spent;
                const ratio = limit > 0 ? (spent / limit) * 100 : 0;
                
                return (
                  <div key={cat} className="grid grid-cols-1 md:grid-cols-12 gap-3 md:gap-4 items-center border-b border-gray-50 pb-4 md:pb-3 last:border-0 last:pb-0 text-xs">
                    {/* 1. Category name */}
                    <div className="col-span-12 md:col-span-3">
                      <span className="font-bold text-gray-800 flex items-center gap-1.5 text-sm md:text-xs">
                        <span className="text-base md:text-sm">{getEmoji(cat)}</span>
                        {cat}
                      </span>
                    </div>

                    {/* 2. Budget Limit inline input */}
                    <div className="col-span-6 md:col-span-2">
                      <div className="flex items-center gap-1">
                        <span className="text-[10px] text-gray-400">RM</span>
                        <input
                          type="number"
                          step="10"
                          min="0"
                          value={limit}
                          onChange={(e) => handleBudgetChange(category, parseFloat(e.target.value) || 0)}
                          className="font-bold text-gray-700 rounded border border-[#cbd5e1] p-1.5 focus:border-[#0F7B6C] w-full font-mono text-xs"
                        />
                      </div>
                    </div>

                    {/* 3. Spent */}
                    <div className="col-span-3 md:col-span-2 font-mono text-gray-600 font-semibold md:text-right">
                      <span className="md:hidden block text-[9px] text-gray-400 font-bold uppercase">SPENT</span>
                      RM {spent.toFixed(2)}
                    </div>

                    {/* 4. Remaining */}
                    <div className="col-span-3 md:col-span-2 font-mono text-gray-600 font-semibold md:text-right">
                      <span className="md:hidden block text-[9px] text-gray-400 font-bold uppercase">REMAINING</span>
                      <span className={remaining < 0 ? 'text-red-600 font-bold' : remaining < (limit * 0.2) ? 'text-amber-500' : 'text-gray-600'}>
                        RM {remaining.toFixed(2)}
                      </span>
                    </div>

                    {/* 5. Progress line */}
                    <div className="col-span-12 md:col-span-3 space-y-1">
                      <div className="relative w-full h-2 bg-gray-100 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full transition-all duration-300 ${
                            ratio >= 100
                              ? 'bg-red-500'
                              : ratio >= 80
                              ? 'bg-amber-500'
                              : 'bg-[#10B981]'
                          }`}
                          style={{ width: `${Math.min(ratio, 100)}%` }}
                        />
                      </div>
                      <div className="flex justify-between text-[10px] font-mono text-gray-400">
                        <span>{ratio.toFixed(0)}% limit used</span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            <div className="p-4 bg-[#f8fffe] border-t border-[#e0f1ee] text-right">
              <button
                type="submit"
                className="w-full sm:w-auto bg-[#0F7B6C] hover:bg-[#0a5c51] text-white px-6 py-2.5 rounded-lg font-bold text-sm transition-colors shadow-md flex items-center justify-center gap-2 block ml-auto"
              >
                <Save className="h-4 w-4" />
                <span>{t.saveAllBudgets}</span>
              </button>
            </div>
          </form>
        </div>
      )}

      {/* History Month Tab */}
      {activeTab === 'history' && (
        <div className="space-y-6">
          <div className="bg-white border border-[#e0f1ee] rounded-xl p-5 shadow-sm">
            <h3 className="text-base font-bold text-gray-800 mb-2 flex items-center gap-2">
              <span className="text-lg">📆</span>
              <span>3-Month spending comparison</span>
            </h3>
            <p className="text-xs text-gray-500 font-mono mb-6">
              Plotly Grouped Bar Chart comparing category targets with April, May, and June spending levels.
            </p>

            <div className="h-[360px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={historyData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                  <XAxis dataKey="category" stroke="#94a3b8" fontSize={11} />
                  <YAxis stroke="#94a3b8" fontSize={11} tickFormatter={(v) => `RM ${v}`} />
                  <Tooltip formatter={(value) => `RM ${parseFloat(value as string).toFixed(2)}`} />
                  <Legend />
                  <Bar dataKey="Budget" fill="#cbd5e1" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="April Actual" fill="#93c5fd" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="May Actual" fill="#fca5a5" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="June Actual" fill="#2dd4bf" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="bg-[#fef3c7] border border-[#fde68a] rounded-xl p-5 flex items-start gap-4">
            <div className="p-2.5 bg-amber-500 text-white rounded-lg">
              <AlertTriangle className="h-5 w-5" />
            </div>
            <div>
              <h4 className="text-sm font-bold text-amber-800 mb-1">Overspend Trend Analysed</h4>
              <p className="text-xs text-gray-600 leading-relaxed">
                Historically, your **Food & Dining** and **Entertainment** budgets are highly vulnerable in May. Check these spikes compared to June limits, buddy. Having Mamak daily adds up quickly! Use standard caps.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
