import React, { useState, useMemo } from 'react';
import { Filter, Trash2, ChevronDown, ChevronUp, Plus, CreditCard, Layers } from 'lucide-react';
import { Transaction, TranslationSet, Category } from '../../types';

interface TransactionsPageProps {
  transactions: Transaction[];
  onUpdateTransaction: (id: string, updatedFields: Partial<Transaction>) => void;
  onDeleteTransactions: (ids: string[]) => void;
  t: TranslationSet;
}

export default function TransactionsPage({
  transactions,
  onUpdateTransaction,
  onDeleteTransactions,
  t
}: TransactionsPageProps) {
  // Filter States
  const [startDate, setStartDate] = useState('2025-06-01');
  const [endDate, setEndDate] = useState('2025-06-30');
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [maxAmount, setMaxAmount] = useState<number>(200);

  // Active Filters (actually applied)
  const [activeFilters, setActiveFilters] = useState({
    startDate: '2025-06-01',
    endDate: '2025-06-30',
    category: 'All',
    maxAmount: 200,
  });

  // Table selection
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  
  // Category Expander
  const [isCategoryExpanderOpen, setIsCategoryExpanderOpen] = useState(false);
  const [customCategories, setCustomCategories] = useState<string[]>([]);
  const [newCategoryName, setNewCategoryName] = useState('');
  const [newCategoryColor, setNewCategoryColor] = useState('#0F7B6C');

  const defaultCategories = ['Food & Dining', 'Transport', 'Shopping', 'Bills', 'Entertainment', 'Other'];
  const allCategories = useMemo(() => {
    return [...defaultCategories, ...customCategories];
  }, [customCategories]);

  // Apply filters
  const handleApplyFilters = () => {
    setActiveFilters({
      startDate,
      endDate,
      category: selectedCategory,
      maxAmount,
    });
    setSelectedIds([]); // Reset select state
  };

  // Process Filtered Transactions
  const filteredTransactions = useMemo(() => {
    return transactions.filter((tx) => {
      const matchDate = tx.date >= activeFilters.startDate && tx.date <= activeFilters.endDate;
      const matchCategory = activeFilters.category === 'All' || tx.category === activeFilters.category;
      const matchAmount = tx.amount <= activeFilters.maxAmount;
      return matchDate && matchCategory && matchAmount;
    });
  }, [transactions, activeFilters]);

  // Calculations per Category for Expander Listing
  const categoryStats = useMemo(() => {
    const stats: { [cat: string]: { total: number; count: number } } = {};
    allCategories.forEach((cat) => {
      stats[cat] = { total: 0, count: 0 };
    });

    transactions.forEach((tx) => {
      if (stats[tx.category]) {
        stats[tx.category].total += tx.amount;
        stats[tx.category].count += 1;
      } else {
        stats[tx.category] = { total: tx.amount, count: 1 };
      }
    });

    return stats;
  }, [transactions, allCategories]);

  // Add custom category
  const handleAddCategory = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newCategoryName.trim()) return;
    if (allCategories.includes(newCategoryName.trim())) return;

    setCustomCategories([...customCategories, newCategoryName.trim()]);
    setNewCategoryName('');
  };

  // Toggle single checkbox selection
  const handleToggleSelectRow = (id: string) => {
    if (selectedIds.includes(id)) {
      setSelectedIds(selectedIds.filter((_id) => _id !== id));
    } else {
      setSelectedIds([...selectedIds, id]);
    }
  };

  // Toggle master select all rows
  const handleToggleSelectAll = () => {
    if (selectedIds.length === filteredTransactions.length) {
      setSelectedIds([]);
    } else {
      setSelectedIds(filteredTransactions.map((tx) => tx.id));
    }
  };

  const handleDeleteSelected = () => {
    if (selectedIds.length === 0) return;
    onDeleteTransactions(selectedIds);
    setSelectedIds([]);
  };

  // Cell updates (st.data_editor replication)
  const handleCellUpdate = (id: string, field: keyof Transaction, val: any) => {
    onUpdateTransaction(id, { [field]: val });
  };

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
          {t.transactions.replace(/^[^\w\s]+/g, '').trim()}
        </h2>
        <p className="text-sm text-gray-500 font-mono">
          Interactive spending table with spreadsheet editing capability.
        </p>
      </div>

      {/* Filter Section Card */}
      <div className="bg-white border border-[#e0f1ee] rounded-xl p-5 shadow-sm space-y-4">
        <h3 className="text-xs font-mono font-bold text-[#0F7B6C] tracking-wider uppercase flex items-center gap-1.5">
          <Filter className="h-4 w-4" />
          <span>{t.filters}</span>
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
          {/* Date range start */}
          <div>
            <label className="text-xs font-semibold text-gray-600 block mb-1">Start Date</label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="w-full text-xs rounded-lg border border-[#cbd5e1] p-2 focus:border-[#0F7B6C] font-mono"
            />
          </div>

          {/* Date range end */}
          <div>
            <label className="text-xs font-semibold text-gray-600 block mb-1">End Date</label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="w-full text-xs rounded-lg border border-[#cbd5e1] p-2 focus:border-[#0F7B6C] font-mono"
            />
          </div>

          {/* Category Select */}
          <div>
            <label className="text-xs font-semibold text-gray-600 block mb-1">Category</label>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="w-full text-xs rounded-lg border border-[#cbd5e1] p-2 focus:border-[#0F7B6C]"
            >
              <option value="All">All Categories</option>
              {allCategories.map((cat) => (
                <option key={cat} value={cat}>
                  {cat}
                </option>
              ))}
            </select>
          </div>

          {/* Amount range slider (manual st.slider simulation) */}
          <div>
            <div className="flex justify-between text-xs font-semibold text-gray-600 mb-1">
              <span>Max Amount (RM)</span>
              <span className="font-mono text-[#0F7B6C]">RM {maxAmount}</span>
            </div>
            <input
              type="range"
              min="5"
              max="500"
              step="5"
              value={maxAmount}
              onChange={(e) => setMaxAmount(parseInt(e.target.value))}
              className="w-full h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-[#0F7B6C]"
            />
          </div>
        </div>

        <button
          onClick={handleApplyFilters}
          className="w-full md:w-auto bg-[#0F7B6C] hover:bg-[#0a5c51] text-white px-5 py-2 rounded-lg font-bold text-xs font-mono transition-colors shadow-sm uppercase tracking-wider block ml-auto"
        >
          {t.applyFilters}
        </button>
      </div>

      {/* Main Data Editor Grid */}
      <div className="bg-white border border-[#e0f1ee] rounded-xl overflow-hidden shadow-sm">
        <div className="p-4 border-b border-[#e0f1ee] bg-[#f8fffe]/50 flex items-center justify-between">
          <span className="text-xs font-mono text-gray-500 font-bold">
            SHOWING {filteredTransactions.length} of {transactions.length} VALUES • double click cells to edit in place
          </span>
          {selectedIds.length > 0 && (
            <button
              onClick={handleDeleteSelected}
              className="flex items-center gap-1.5 bg-red-50 hover:bg-red-100 text-red-600 border border-red-200 text-xs font-bold font-mono px-3 py-1.5 rounded-lg transition-colors"
            >
              <Trash2 className="h-3.5 w-3.5" />
              <span>{t.deleteSelected} ({selectedIds.length})</span>
            </button>
          )}
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-[#e0f1ee] bg-[#f8fffe]/30 text-xs font-mono text-[#0a5c51]/80">
                <th className="p-3 w-10 text-center">
                  <input
                    type="checkbox"
                    checked={filteredTransactions.length > 0 && selectedIds.length === filteredTransactions.length}
                    onChange={handleToggleSelectAll}
                    className="rounded text-[#0F7B6C] focus:ring-[#0F7B6C]"
                  />
                </th>
                <th className="p-3 font-semibold w-24">Date</th>
                <th className="p-3 font-semibold">Merchant</th>
                <th className="p-3 font-semibold">Category</th>
                <th className="p-3 font-semibold text-right w-32">Amount</th>
                <th className="p-3 font-semibold text-center w-24">Source</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 text-xs">
              {filteredTransactions.length === 0 ? (
                <tr>
                  <td colSpan={6} className="p-8 text-center text-gray-400 font-mono text-xs">
                    No transactions match current filters.
                  </td>
                </tr>
              ) : (
                filteredTransactions.map((tx) => (
                  <tr
                    key={tx.id}
                    className={`hover:bg-[#f8fffe]/20 group transition-colors ${
                      selectedIds.includes(tx.id) ? 'bg-[#0f7b6c]/5' : ''
                    }`}
                  >
                    {/* Checkbox selector */}
                    <td className="p-3 text-center">
                      <input
                        type="checkbox"
                        checked={selectedIds.includes(tx.id)}
                        onChange={() => handleToggleSelectRow(tx.id)}
                        className="rounded text-[#0F7B6C] focus:ring-[#0F7B6C]"
                      />
                    </td>

                    {/* Date Input */}
                    <td className="p-2">
                      <input
                        type="text"
                        value={tx.date}
                        onChange={(e) => handleCellUpdate(tx.id, 'date', e.target.value)}
                        className="font-mono text-gray-700 w-full bg-transparent hover:bg-gray-50 border border-transparent hover:border-gray-200 focus:border-[#0F7B6C] focus:bg-white rounded p-1 transition-all"
                      />
                    </td>

                    {/* Merchant text Input */}
                    <td className="p-2 font-medium">
                      <input
                        type="text"
                        value={tx.merchant}
                        onChange={(e) => handleCellUpdate(tx.id, 'merchant', e.target.value)}
                        className="font-semibold text-gray-800 w-full bg-transparent hover:bg-gray-50 border border-transparent hover:border-gray-200 focus:border-[#0F7B6C] focus:bg-white rounded p-1 transition-all"
                      />
                    </td>

                    {/* Category select inside table */}
                    <td className="p-2">
                      <select
                        value={tx.category}
                        onChange={(e) => handleCellUpdate(tx.id, 'category', e.target.value)}
                        className="w-full text-xs font-semibold bg-transparent hover:bg-gray-50 border border-transparent hover:border-gray-200 focus:border-[#0F7B6C] focus:bg-white rounded p-1 transition-all"
                      >
                        {allCategories.map((c) => (
                          <option key={c} value={c}>
                            {c}
                          </option>
                        ))}
                      </select>
                    </td>

                    {/* Amount double inputs */}
                    <td className="p-2 text-right font-bold font-mono">
                      <div className="flex items-center justify-end">
                        <span className="text-[10px] text-gray-400 mr-1">RM</span>
                        <input
                          type="number"
                          step="0.01"
                          value={tx.amount}
                          onChange={(e) => handleCellUpdate(tx.id, 'amount', parseFloat(e.target.value) || 0)}
                          className="font-bold text-right text-gray-800 bg-transparent hover:bg-gray-50 border border-transparent hover:border-gray-200 focus:border-[#0F7B6C] focus:bg-white rounded p-1 w-20 transition-all font-mono"
                        />
                      </div>
                    </td>

                    {/* Source label */}
                    <td className="p-3 text-center">
                      <span
                        className={`inline-block px-2 py-0.5 rounded text-[10px] uppercase font-bold font-mono ${
                          tx.source === 'ocr'
                            ? 'bg-[#0f7b6c]/10 text-[#0F7B6C] border border-[#0F7B6C]/20'
                            : 'bg-gray-100 text-gray-600 border border-gray-200'
                        }`}
                      >
                        {tx.source}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Expander component section mimicking Streamlit st.expander */}
      <div className="bg-white border border-[#e0f1ee] rounded-xl overflow-hidden shadow-sm">
        <button
          onClick={() => setIsCategoryExpanderOpen(!isCategoryExpanderOpen)}
          className="w-full flex items-center justify-between p-4 bg-[#f8fffe]/50 hover:bg-[#f8fffe] transition-colors text-sm font-bold text-gray-800"
        >
          <div className="flex items-center gap-2">
            <Layers className="h-4 w-4 text-[#0F7B6C]" />
            <span>{t.manageCategories}</span>
          </div>
          {isCategoryExpanderOpen ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
        </button>

        {isCategoryExpanderOpen && (
          <div className="p-5 border-t border-[#e0f1ee] space-y-6 animate-fade-in text-xs text-gray-700">
            
            {/* List all active categories */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {allCategories.map((cat) => {
                const isDefault = defaultCategories.includes(cat);
                const stats = categoryStats[cat] || { total: 0, count: 0 };
                return (
                  <div key={cat} className="p-3 rounded-lg border border-gray-100 bg-gray-50/50 flex flex-col justify-between">
                    <div className="flex justify-between items-center mb-1">
                      <span className="font-semibold text-gray-800 flex items-center gap-1">
                        <span>{getEmoji(cat)}</span>
                        {cat}
                      </span>
                      {isDefault ? (
                        <span className="text-[10px] text-gray-400 font-mono">System Default</span>
                      ) : (
                        <span className="text-[10px] text-[#0F7B6C] font-mono font-bold">Custom</span>
                      )}
                    </div>
                    <div className="flex justify-between items-end mt-2">
                      <span className="text-gray-500 font-mono">RM {stats.total.toFixed(2)} spent</span>
                      <span className="text-gray-400 font-mono">{stats.count} transactions</span>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Add Custom Category form */}
            <form onSubmit={handleAddCategory} className="border-t border-gray-100 pt-4 space-y-3">
              <h4 className="font-bold text-gray-800">Add custom spending category</h4>
              <div className="flex flex-col sm:flex-row gap-3">
                <input
                  type="text"
                  required
                  placeholder="e.g. Subscriptions / Books"
                  value={newCategoryName}
                  onChange={(e) => setNewCategoryName(e.target.value)}
                  className="rounded-lg border border-[#cbd5e1] p-2 text-xs focus:border-[#0F7B6C] flex-1"
                />
                <div className="flex items-center gap-2">
                  <label className="text-[10px] font-mono text-gray-500">Pick color accent:</label>
                  <input
                    type="color"
                    value={newCategoryColor}
                    onChange={(e) => setNewCategoryColor(e.target.value)}
                    className="w-10 h-8 rounded border p-0.5 cursor-pointer"
                  />
                  <button
                    type="submit"
                    className="bg-[#0F7B6C] hover:bg-[#0a5c51] text-white font-bold text-xs font-mono py-2 px-4 rounded-lg flex items-center gap-1 shadow-sm shrink-0"
                  >
                    <Plus className="h-3 w-3" />
                    <span>Create Category</span>
                  </button>
                </div>
              </div>
            </form>
          </div>
        )}
      </div>
    </div>
  );
}
