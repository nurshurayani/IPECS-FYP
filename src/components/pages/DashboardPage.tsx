import { useMemo } from 'react';
import { ResponsiveContainer, PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, Legend } from 'recharts';
import { ArrowUpRight, AlertCircle, Sparkles, Receipt } from 'lucide-react';
import { Transaction, Budgets, Alert, TranslationSet } from '../../types';

interface DashboardPageProps {
  transactions: Transaction[];
  budgets: Budgets;
  alerts: Alert[];
  setActiveTab: (tab: string) => void;
  t: TranslationSet;
}

export default function DashboardPage({ transactions, budgets, alerts, setActiveTab, t }: DashboardPageProps) {
  // Current active month in system is June 2025 (based on pre-loaded transactions)
  const currentMonthStr = '2025-06';

  // 1. Calculations
  const totalBudget = useMemo(() => {
    return Object.values(budgets).reduce((sum, val) => sum + val, 0);
  }, [budgets]);

  const totalSpentThisMonth = useMemo(() => {
    return transactions
      .filter((tx) => tx.date.startsWith(currentMonthStr))
      .reduce((sum, tx) => sum + tx.amount, 0);
  }, [transactions]);

  const budgetRemaining = useMemo(() => {
    return totalBudget - totalSpentThisMonth;
  }, [totalBudget, totalSpentThisMonth]);

  const budgetRemainingPercentage = useMemo(() => {
    return totalBudget > 0 ? (budgetRemaining / totalBudget) * 100 : 0;
  }, [totalBudget, budgetRemaining]);

  const transactionsThisWeek = useMemo(() => {
    // Let's count transactions in latest dates of June 2025 (e.g. June 12 to June 18, 2025)
    return transactions.filter((tx) => {
      const txDate = new Date(tx.date);
      const startDate = new Date('2025-06-12');
      const endDate = new Date('2025-06-18');
      return txDate >= startDate && txDate <= endDate;
    }).length;
  }, [transactions]);

  const activeAlertsCount = useMemo(() => {
    return alerts.filter((a) => !a.dismissed).length;
  }, [alerts]);

  // 2. Plotly Donut Chart Simulation (Teal Palette)
  const categorySpendingData = useMemo(() => {
    const counts: { [cat: string]: number } = {};
    transactions
      .filter((tx) => tx.date.startsWith(currentMonthStr))
      .forEach((tx) => {
        counts[tx.category] = (counts[tx.category] || 0) + tx.amount;
      });

    return Object.keys(budgets).map((cat) => ({
      name: cat,
      value: parseFloat((counts[cat] || 0).toFixed(2)),
    }));
  }, [transactions, budgets]);

  const TEAL_PALETTE = ['#0F7B6C', '#1EA896', '#32BCA9', '#5CD2C3', '#96E7DC', '#C8F3EE'];

  // 3. Horizontal Bar Chart Simulation (Budget vs Actual)
  const budgetVsActualData = useMemo(() => {
    const counts: { [cat: string]: number } = {};
    transactions
      .filter((tx) => tx.date.startsWith(currentMonthStr))
      .forEach((tx) => {
        counts[tx.category] = (counts[tx.category] || 0) + tx.amount;
      });

    return Object.keys(budgets).map((cat) => {
      const actual = parseFloat((counts[cat] || 0).toFixed(2));
      const budget = budgets[cat as keyof Budgets] || 0;
      const pct = budget > 0 ? (actual / budget) * 100 : 0;

      // Color mapping
      let color = '#10B981'; // Green
      if (pct >= 100) {
        color = '#EF4444'; // Red
      } else if (pct >= 80) {
        color = '#F59E0B'; // Amber
      }

      return {
        name: cat,
        Budget: budget,
        Actual: actual,
        color: color,
        percentage: pct,
      };
    });
  }, [transactions, budgets]);

  // 4. Last 5 transactions
  const recentTxs = useMemo(() => {
    return [...transactions]
      .sort((a, b) => b.date.localeCompare(a.date))
      .slice(0, 5);
  }, [transactions]);

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
    <div className="space-y-8 animate-fade-in">
      {/* Title block */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#e0f1ee] pb-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-800 font-sans tracking-tight">
            {t.dashboard.replace(/^[^\w\s]+/g, '').trim()}
          </h2>
          <p className="text-sm text-gray-500 font-mono">
            IPECS {currentMonthStr === '2025-06' ? '• June 2025' : ''}
          </p>
        </div>
        <div>
          <button
            onClick={() => setActiveTab('receipt_entry')}
            className="flex items-center gap-2 bg-[#0F7B6C] hover:bg-[#0a5c51] text-white px-5 py-2.5 rounded-lg font-medium text-sm transition-all duration-150 shadow-md hover:shadow-lg hover:shadow-[#0F7B6C]/20"
          >
            <Receipt className="h-4 w-4" />
            <span>{t.uploadReceipt}</span>
          </button>
        </div>
      </div>

      {/* Row 1 — 4 st.metric style cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Metric 1 */}
        <div className="bg-white border border-[#e0f1ee] rounded-xl p-5 shadow-sm transition-all hover:shadow-md hover:border-[#b4e2da]">
          <span className="text-xs font-mono font-bold text-gray-400 tracking-wider uppercase block mb-1">
            {t.totalSpentThisMonth}
          </span>
          <div className="flex items-baseline gap-1">
            <span className="text-xs font-bold text-[#0F7B6C]">RM</span>
            <span className="text-2xl font-bold font-mono text-gray-800">
              {totalSpentThisMonth.toLocaleString('en-MY', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </span>
          </div>
          <span className="text-xs text-[#0F7B6C] font-semibold mt-2 inline-flex items-center gap-1 bg-[#0F7B6C]/10 px-2 py-0.5 rounded-md">
            <ArrowUpRight className="h-3 w-3" />
            {currentMonthStr === '2025-06' ? 'June 2025' : ''}
          </span>
        </div>

        {/* Metric 2 */}
        <div className="bg-white border border-[#e0f1ee] rounded-xl p-5 shadow-sm transition-all hover:shadow-md hover:border-[#b4e2da]">
          <span className="text-xs font-mono font-bold text-gray-400 tracking-wider uppercase block mb-1">
            {t.budgetRemaining}
          </span>
          <div className="flex items-baseline gap-1">
            <span className="text-xs font-bold text-[#0F7B6C]">RM</span>
            <span className="text-2xl font-bold font-mono text-gray-800">
              {budgetRemaining.toLocaleString('en-MY', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </span>
          </div>
          {budgetRemainingPercentage < 20 ? (
            <span className="text-xs text-red-500 font-bold mt-2 inline-flex items-center gap-1 bg-red-50 px-2 py-0.5 rounded-md animate-pulse">
              ⚠️ {budgetRemainingPercentage.toFixed(1)}% remaining!
            </span>
          ) : (
            <span className="text-xs text-green-600 font-semibold mt-2 inline-flex items-center gap-1 bg-green-50 px-2 py-0.5 rounded-md">
              ✅ {budgetRemainingPercentage.toFixed(1)}% remaining
            </span>
          )}
        </div>

        {/* Metric 3 */}
        <div className="bg-white border border-[#e0f1ee] rounded-xl p-5 shadow-sm transition-all hover:shadow-md hover:border-[#b4e2da]">
          <span className="text-xs font-mono font-bold text-gray-400 tracking-wider uppercase block mb-1">
            {t.txThisWeek}
          </span>
          <div className="flex items-baseline gap-1">
            <span className="text-2xl font-bold font-mono text-gray-800">
              {transactionsThisWeek}
            </span>
            <span className="text-xs text-gray-400 font-medium">txs</span>
          </div>
          <span className="text-xs text-blue-600 font-semibold mt-2 inline-flex items-center gap-1 bg-blue-50 px-2 py-0.5 rounded-md">
            📚 Past 7 Days
          </span>
        </div>

        {/* Metric 4 */}
        <div className="bg-white border border-[#e0f1ee] rounded-xl p-5 shadow-sm transition-all hover:shadow-md hover:border-[#b4e2da]">
          <span className="text-xs font-mono font-bold text-gray-400 tracking-wider uppercase block mb-1">
            {t.activeAlerts}
          </span>
          <div className="flex items-baseline gap-1">
            <span className={`text-2xl font-bold font-mono ${activeAlertsCount > 0 ? 'text-red-600' : 'text-gray-800'}`}>
              {activeAlertsCount}
            </span>
            <span className="text-xs text-gray-400 font-medium">anomalies</span>
          </div>
          {activeAlertsCount > 0 ? (
            <span
              onClick={() => setActiveTab('forecast_alerts')}
              className="cursor-pointer text-xs text-red-500 font-bold mt-2 inline-flex items-center gap-1 bg-red-50 hover:bg-red-100 px-2 py-0.5 rounded-md transition-all animate-pulse"
            >
              <AlertCircle className="h-3 w-3" />
              Action required!
            </span>
          ) : (
            <span className="text-xs text-green-600 font-semibold mt-2 inline-flex items-center gap-1 bg-green-50 px-2 py-0.5 rounded-md">
              ✨ Account safe
            </span>
          )}
        </div>
      </div>

      {/* Row 2 — Donut chart and Horizontal budget comparison */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column: Spending by Category */}
        <div className="bg-white border border-[#e0f1ee] rounded-xl p-5 shadow-sm">
          <h3 className="text-base font-bold text-gray-800 mb-4 flex items-center gap-2">
            <span className="text-lg">🍩</span>
            {t.spendingByCategory}
          </h3>
          <div className="h-[280px]">
            {totalSpentThisMonth === 0 ? (
              <div className="h-full flex items-center justify-center text-gray-400 font-mono text-sm">
                No spending recorded for this period
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={categorySpendingData.filter(d => d.value > 0)}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={90}
                    paddingAngle={3}
                    dataKey="value"
                    label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                  >
                    {categorySpendingData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={TEAL_PALETTE[index % TEAL_PALETTE.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => `RM ${parseFloat(value as string).toFixed(2)}`} />
                </PieChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        {/* Right Column: Budget vs Actual horizontal bars */}
        <div className="bg-white border border-[#e0f1ee] rounded-xl p-5 shadow-sm">
          <h3 className="text-base font-bold text-gray-800 mb-4 flex items-center gap-2">
            <span className="text-lg">📊</span>
            {t.budgetVsActual}
          </h3>
          <div className="h-[280px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={budgetVsActualData}
                layout="vertical"
                margin={{ top: 5, right: 30, left: 40, bottom: 5 }}
              >
                <XAxis type="number" stroke="#94a3b8" fontSize={11} tickFormatter={(v) => `RM ${v}`} />
                <YAxis dataKey="name" type="category" stroke="#94a3b8" fontSize={11} width={100} />
                <Tooltip formatter={(value) => `RM ${parseFloat(value as string).toFixed(2)}`} />
                <Legend />
                <Bar dataKey="Actual" radius={[0, 4, 4, 0]}>
                  {budgetVsActualData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
                <Bar dataKey="Budget" fill="#cbd5e1" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="flex justify-center gap-4 mt-2 text-xs font-mono">
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 bg-[#10B981] rounded-full" />
              <span>Under 80%</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 bg-[#F59E0B] rounded-full" />
              <span>80% - 99%</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 bg-[#EF4444] rounded-full" />
              <span>Over Budget (100%+)</span>
            </div>
          </div>
        </div>
      </div>

      {/* Row 3 — Recent Transactions */}
      <div className="bg-white border border-[#e0f1ee] rounded-xl p-6 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-base font-bold text-gray-800 flex items-center gap-2">
            <span className="text-lg">📋</span>
            {t.recentTransactions}
          </h3>
          <button
            onClick={() => setActiveTab('transactions')}
            className="text-xs font-bold text-[#0F7B6C] hover:text-[#0a5c51] uppercase font-mono tracking-wider flex items-center gap-1"
          >
            {t.viewAll} &rarr;
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left interface-table">
            <thead>
              <tr className="border-b border-[#e0f1ee] bg-[#f8fffe]/50 text-xs font-mono text-[#0a5c51]/80">
                <th className="p-3 font-semibold">{t.dateLabel}</th>
                <th className="p-3 font-semibold">{t.merchantName}</th>
                <th className="p-3 font-semibold">{t.categoryLabel}</th>
                <th className="p-3 font-semibold text-right">{t.amountLabel}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#e0f1ee] text-sm text-gray-700">
              {recentTxs.map((tx) => (
                <tr key={tx.id} className="hover:bg-gray-50/50 transition-colors">
                  <td className="p-3 font-mono text-xs">{tx.date}</td>
                  <td className="p-3 font-semibold">{tx.merchant}</td>
                  <td className="p-3">
                    <span className="inline-flex items-center gap-1.5 px-2 py-1 rounded-full text-xs font-medium bg-[#f0fdfa] text-[#0f7b6c] border border-[#e0f1ee]">
                      <span className="text-sm">{getEmoji(tx.category)}</span>
                      {tx.category}
                    </span>
                  </td>
                  <td className="p-3 text-right font-bold font-mono">
                    RM {tx.amount.toFixed(2)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Malasyian budget tip card */}
      <div className="bg-[#f0fdfa] border border-[#b4e2da] rounded-xl p-5 flex items-start gap-4">
        <div className="p-2.5 bg-[#0F7B6C] text-white rounded-lg">
          <Sparkles className="h-5 w-5" />
        </div>
        <div>
          <h4 className="text-sm font-bold text-[#0a5c51] mb-1">Mamak Financial Wisdom</h4>
          <p className="text-xs text-gray-600 leading-relaxed">
            Mamak session costs RM10 to RM15 per seating. Eating at Mamak daily adds up to RM300/month. Manage your "Food & Dining" budget wisely, buddy! Check "AI Forecast & Alerts" tab for customized budget predictions!
          </p>
        </div>
      </div>
    </div>
  );
}
