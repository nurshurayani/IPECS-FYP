import { useState, useMemo } from 'react';
import { ResponsiveContainer, LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, Tooltip, Legend } from 'recharts';
import { Sparkles, Calendar, TrendingUp, Download, PieChart as PieIcon, List } from 'lucide-react';
import { Transaction, TranslationSet } from '../../types';

interface ReportsPageProps {
  transactions: Transaction[];
  t: TranslationSet;
}

export default function ReportsPage({ transactions, t }: ReportsPageProps) {
  const [period, setPeriod] = useState<'this_month' | 'last_month' | 'last_3_months' | 'custom'>('this_month');
  const [startDate, setStartDate] = useState('2025-06-01');
  const [endDate, setEndDate] = useState('2025-06-18');

  // 1. Process Date Range based on period selection
  const activeRange = useMemo(() => {
    switch (period) {
      case 'this_month':
        return { start: '2025-06-01', end: '2025-06-30' };
      case 'last_month':
        return { start: '2025-05-01', end: '2025-05-31' };
      case 'last_3_months':
        return { start: '2025-04-01', end: '2025-06-30' };
      case 'custom':
      default:
        return { start: startDate, end: endDate };
    }
  }, [period, startDate, endDate]);

  // 2. Filter Transactions for current selection
  const filteredTxs = useMemo(() => {
    return transactions.filter((tx) => tx.date >= activeRange.start && tx.date <= activeRange.end);
  }, [transactions, activeRange]);

  // 3. Dynamic metrics row calculations
  const summaryMetrics = useMemo(() => {
    if (filteredTxs.length === 0) {
      return { total: 0, highestCategory: '-', mostFrequentMerchant: '-', avgDaily: 0 };
    }

    // Total Spent
    const total = filteredTxs.reduce((sum, tx) => sum + tx.amount, 0);

    // Highest Category
    const categorySumMap: { [cat: string]: number } = {};
    filteredTxs.forEach((tx) => {
      categorySumMap[tx.category] = (categorySumMap[tx.category] || 0) + tx.amount;
    });

    let highestCat = '-';
    let highestAmt = 0;
    Object.entries(categorySumMap).forEach(([cat, amt]) => {
      if (amt > highestAmt) {
        highestAmt = amt;
        highestCat = cat;
      }
    });

    // Most Frequent Merchant
    const merchantCountMap: { [merch: string]: number } = {};
    filteredTxs.forEach((tx) => {
      merchantCountMap[tx.merchant] = (merchantCountMap[tx.merchant] || 0) + 1;
    });

    let modalMerch = '-';
    let modalCt = 0;
    Object.entries(merchantCountMap).forEach(([merch, ct]) => {
      if (ct > modalCt) {
        modalCt = ct;
        modalMerch = merch;
      }
    });

    // Average Daily spending
    const dates = filteredTxs.map((tx) => tx.date);
    const uniqueDates = Array.from(new Set(dates));
    const daysInPeriod = uniqueDates.length > 0 ? uniqueDates.length : 1;
    const avgDaily = total / daysInPeriod;

    return {
      total,
      highestCategory: highestCat,
      mostFrequentMerchant: modalMerch,
      avgDaily,
    };
  }, [filteredTxs]);

  // 4. Line Chart: Daily Trend
  const dailyTrendData = useMemo(() => {
    const trendMap: { [date: string]: number } = {};
    // Ensure chronological sorting of base dates
    filteredTxs.forEach((tx) => {
      trendMap[tx.date] = (trendMap[tx.date] || 0) + tx.amount;
    });

    return Object.entries(trendMap)
      .sort(([d1], [d2]) => d1.localeCompare(d2))
      .map(([date, amount]) => ({
        date: date.substring(5), // Keep MM-DD for brevity
        Amount: parseFloat(amount.toFixed(2)),
      }));
  }, [filteredTxs]);

  // 5. Total Spent per Category Bar Chart & Pie Chart data
  const categoryChartData = useMemo(() => {
    const sums: { [cat: string]: number } = {};
    filteredTxs.forEach((tx) => {
      sums[tx.category] = (sums[tx.category] || 0) + tx.amount;
    });

    return Object.entries(sums).map(([category, amount]) => ({
      name: category,
      value: parseFloat(amount.toFixed(2)),
    }));
  }, [filteredTxs]);

  // Colors palette
  const TEAL_PALETTE = ['#0F7B6C', '#1EA896', '#32BCA9', '#5CD2C3', '#96E7DC', '#cbd5e1'];

  // 6. Category Breakdown Table data
  const categoryBreakdownTable = useMemo(() => {
    const counts: { [cat: string]: number } = {};
    const sums: { [cat: string]: number } = {};

    filteredTxs.forEach((tx) => {
      counts[tx.category] = (counts[tx.category] || 0) + 1;
      sums[tx.category] = (sums[tx.category] || 0) + tx.amount;
    });

    const grandTotal = summaryMetrics.total;

    return Object.keys(sums).map((cat) => {
      const sum = sums[cat] || 0;
      const count = counts[cat] || 0;
      const pct = grandTotal > 0 ? (sum / grandTotal) * 100 : 0;
      const avg = count > 0 ? sum / count : 0;

      return {
        category: cat,
        total: sum,
        percentage: pct,
        count,
        avg,
      };
    }).sort((a, b) => b.total - a.total);
  }, [filteredTxs, summaryMetrics.total]);

  // 7. Top 5 Merchants table
  const topMerchantsTable = useMemo(() => {
    const counts: { [merch: string]: number } = {};
    const sums: { [merch: string]: number } = {};

    filteredTxs.forEach((tx) => {
      counts[tx.merchant] = (counts[tx.merchant] || 0) + 1;
      sums[tx.merchant] = (sums[tx.merchant] || 0) + tx.amount;
    });

    return Object.keys(sums).map((merch) => ({
      merchantName: merch,
      total: sums[merch] || 0,
      count: counts[merch] || 0,
    }))
      .sort((a, b) => b.total - a.total)
      .slice(0, 5);
  }, [filteredTxs]);

  // 8. Download filtered transactions as real exportable CSV file
  const handleDownloadCsv = () => {
    if (filteredTxs.length === 0) return;

    // Convert transaction items to CSV string format
    const headers = ['ID', 'Merchant', 'Amount (RM)', 'Date', 'Category', 'Notes', 'Source'];
    const rows = filteredTxs.map((tx) => [
      tx.id,
      `"${tx.merchant.replace(/"/g, '""')}"`,
      tx.amount.toFixed(2),
      tx.date,
      tx.category,
      `"${(tx.notes || '').replace(/"/g, '""')}"`,
      tx.source,
    ]);

    const csvContent =
      'data:text/csv;charset=utf-8,' +
      [headers.join(','), ...rows.map((row) => row.join(','))].join('\n');

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `ipecs_expense_report_${activeRange.start}_to_${activeRange.end}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Title */}
      <div className="border-b border-[#e0f1ee] pb-4">
        <h2 className="text-2xl font-bold text-gray-800 font-sans tracking-tight">
          {t.reports.replace(/^[^\w\s]+/g, '').trim()}
        </h2>
        <p className="text-sm text-gray-500 font-mono">
          Interactive historical metrics and downloadable CSV sheets.
        </p>
      </div>

      {/* Period selector */}
      <div className="bg-white border border-[#e0f1ee] rounded-xl p-5 shadow-sm space-y-4">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h3 className="text-xs font-mono font-bold text-[#0F7B6C] tracking-wider uppercase flex items-center gap-1.5 mb-1">
              <Calendar className="h-4 w-4" />
              <span>SPENDING REPORT PERIOD</span>
            </h3>
            <p className="text-xs text-gray-400 font-mono">Choose a timeframe to slice data.</p>
          </div>

          <div className="flex gap-2 shrink-0 flex-wrap">
            {/* st.radio mimic button toggles */}
            {[
              { id: 'this_month', label: 'This Month (June)' },
              { id: 'last_month', label: 'Last Month (May)' },
              { id: 'last_3_months', label: 'Last 3 Months' },
              { id: 'custom', label: 'Custom Range' },
            ].map((pOption) => (
              <button
                key={pOption.id}
                onClick={() => setPeriod(pOption.id as any)}
                className={`px-4 py-2 rounded-lg text-xs font-bold font-mono transition-all duration-150 ${
                  period === pOption.id
                    ? 'bg-[#0F7B6C] text-white shadow-sm'
                    : 'bg-gray-100 hover:bg-gray-200 text-gray-600'
                }`}
              >
                {pOption.label}
              </button>
            ))}
          </div>
        </div>

        {/* Custom date pickers if Selected */}
        {period === 'custom' && (
          <div className="grid grid-cols-2 gap-4 max-w-md pt-3 border-t border-gray-100 animate-fade-in">
            <div>
              <label className="text-[10px] font-mono text-gray-500 block mb-1">START DATE</label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="w-full text-xs rounded-lg border border-[#cbd5e1] p-2 focus:border-[#0F7B6C] font-mono"
              />
            </div>
            <div>
              <label className="text-[10px] font-mono text-gray-500 block mb-1">END DATE</label>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="w-full text-xs rounded-lg border border-[#cbd5e1] p-2 focus:border-[#0F7B6C] font-mono"
              />
            </div>
          </div>
        )}
      </div>

      {/* Metrics Row st.columns(4) */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white border border-[#e0f1ee] rounded-xl p-5 shadow-sm">
          <span className="text-[10px] font-mono font-bold text-gray-400 block mb-1">TOTAL SPENT</span>
          <p className="text-xl font-bold font-mono text-gray-800">
            RM {summaryMetrics.total.toLocaleString('en-MY', { minimumFractionDigits: 2 })}
          </p>
        </div>

        <div className="bg-white border border-[#e0f1ee] rounded-xl p-5 shadow-sm">
          <span className="text-[10px] font-mono font-bold text-gray-400 block mb-1">HIGHEST CATEGORY</span>
          <p className="text-sm font-bold text-[#0F7B6C] truncate mt-1">
            {summaryMetrics.highestCategory}
          </p>
        </div>

        <div className="bg-white border border-[#e0f1ee] rounded-xl p-5 shadow-sm">
          <span className="text-[10px] font-mono font-bold text-gray-400 block mb-1">MOST FREQUENT MERCHANT</span>
          <p className="text-sm font-bold text-gray-800 truncate mt-1">
            {summaryMetrics.mostFrequentMerchant}
          </p>
        </div>

        <div className="bg-white border border-[#e0f1ee] rounded-xl p-5 shadow-sm">
          <span className="text-[10px] font-mono font-bold text-gray-400 block mb-1">AVG DAILY SPEND</span>
          <p className="text-xl font-bold font-mono text-gray-800">
            RM {summaryMetrics.avgDaily.toLocaleString('en-MY', { minimumFractionDigits: 2 })}
          </p>
        </div>
      </div>

      {/* Check null spending states */}
      {filteredTxs.length === 0 ? (
        <div className="bg-white border border-[#e0f1ee] rounded-xl p-12 text-center text-gray-400 font-mono text-sm">
          No data sheets available for selected period. Choose in-budget June/May ranges!
        </div>
      ) : (
        <>
          {/* Daily spending trend line chart */}
          <div className="bg-white border border-[#e0f1ee] rounded-xl p-5 shadow-sm">
            <h3 className="text-sm font-bold text-gray-800 mb-4 flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-[#0F7B6C]" />
              <span>{t.dailySpendingTrend}</span>
            </h3>
            <div className="h-[240px]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={dailyTrendData}>
                  <XAxis dataKey="date" stroke="#94a3b8" fontSize={11} />
                  <YAxis stroke="#94a3b8" fontSize={11} tickFormatter={(v) => `RM ${v}`} />
                  <Tooltip formatter={(value) => `RM ${value}`} />
                  <Line type="monotone" dataKey="Amount" stroke="#0F7B6C" strokeWidth={2.5} dot={{ r: 4 }} activeDot={{ r: 6 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Charts Row: Bar and Pie side-by-side */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white border border-[#e0f1ee] rounded-xl p-5 shadow-sm">
              <h3 className="text-xs font-mono font-bold text-gray-400 tracking-wider uppercase mb-4">
                {t.totalSpentCategory}
              </h3>
              <div className="h-[240px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={categoryChartData}>
                    <XAxis dataKey="name" stroke="#94a3b8" fontSize={10} />
                    <YAxis stroke="#94a3b8" fontSize={11} tickFormatter={(v) => `RM ${v}`} />
                    <Tooltip formatter={(value) => `RM ${value}`} />
                    <Bar dataKey="value" fill="#0F7B6C" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="bg-white border border-[#e0f1ee] rounded-xl p-5 shadow-sm">
              <h3 className="text-xs font-mono font-bold text-gray-400 tracking-wider uppercase mb-4">
                {t.percentBreakdown}
              </h3>
              <div className="h-[240px]">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={categoryChartData} cx="50%" cy="50%" outerRadius={80} paddingAngle={2} dataKey="value" label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}>
                      {categoryChartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={TEAL_PALETTE[index % TEAL_PALETTE.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => `RM ${value}`} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Breakdown Tables rows */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Category breakdown sheet */}
            <div className="bg-white border border-[#e0f1ee] rounded-xl p-5 shadow-sm lg:col-span-7">
              <h3 className="text-xs font-mono font-bold text-gray-400 tracking-wider uppercase mb-4 flex items-center gap-1.5">
                <List className="h-4 w-4 text-[#0F7B6C]" />
                <span>CATEGORY ANALYTICAL BREAKDOWN</span>
              </h3>
              <div className="overflow-x-auto text-xs">
                <table className="w-full text-left font-mono">
                  <thead>
                    <tr className="border-b border-gray-100 bg-gray-50/50 text-gray-500">
                      <th className="p-2 font-bold uppercase">Category</th>
                      <th className="p-2 font-bold text-right uppercase">Total</th>
                      <th className="p-2 font-bold text-right uppercase">% Total</th>
                      <th className="p-2 font-bold text-center uppercase">Count</th>
                      <th className="p-2 font-bold text-right uppercase">Avg/Tx</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-50">
                    {categoryBreakdownTable.map((row) => (
                      <tr key={row.category} className="hover:bg-gray-50/50">
                        <td className="p-2 font-sans font-bold">{row.category}</td>
                        <td className="p-2 text-right">RM {row.total.toFixed(2)}</td>
                        <td className="p-2 text-right">{row.percentage.toFixed(1)}%</td>
                        <td className="p-2 text-center text-gray-500 font-semibold">{row.count}</td>
                        <td className="p-2 text-right text-gray-500">RM {row.avg.toFixed(2)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Top 5 merchants card */}
            <div className="bg-white border border-[#e0f1ee] rounded-xl p-5 shadow-sm lg:col-span-5">
              <h3 className="text-xs font-mono font-bold text-gray-400 tracking-wider uppercase mb-4 flex items-center gap-1.5">
                <PieIcon className="h-4 w-4 text-[#0F7B6C]" />
                <span>TOP 5 MERCHANTS SPENT</span>
              </h3>
              <div className="overflow-x-auto text-xs">
                <table className="w-full text-left font-mono">
                  <thead>
                    <tr className="border-b border-gray-100 bg-gray-50/50 text-gray-500">
                      <th className="p-2 font-bold uppercase">Merchant</th>
                      <th className="p-2 font-bold text-right uppercase">Total Spent</th>
                      <th className="p-2 font-bold text-center uppercase">Visits</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-50">
                    {topMerchantsTable.map((row) => (
                      <tr key={row.merchantName} className="hover:bg-gray-50/50">
                        <td className="p-2 font-sans font-bold truncate max-w-[120px]">{row.merchantName}</td>
                        <td className="p-2 text-right text-[#0F7B6C] font-bold">RM {row.total.toFixed(2)}</td>
                        <td className="p-2 text-center text-gray-500 font-semibold">{row.count} times</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          {/* Export Action Card */}
          <div className="bg-white border border-[#e0f1ee] rounded-xl p-4 flex flex-col sm:flex-row justify-between items-center gap-3">
            <span className="text-xs font-mono text-gray-500 font-medium">
              Want offline backup? Export sheet of {filteredTxs.length} filtered records directly!
            </span>
            <button
              onClick={handleDownloadCsv}
              className="flex items-center gap-2 bg-[#0F7B6C] hover:bg-[#0a5c51] text-white px-5 py-2.5 rounded-lg text-xs font-bold font-mono transition-colors shadow-sm uppercase tracking-wider block ml-auto"
            >
              <Download className="h-4 w-4" />
              <span>{t.downloadCsv}</span>
            </button>
          </div>
        </>
      )}
    </div>
  );
}
