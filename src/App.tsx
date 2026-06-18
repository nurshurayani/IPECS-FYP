import { useState } from 'react';
import Sidebar from './components/Sidebar';
import DashboardPage from './components/pages/DashboardPage';
import ReceiptEntryPage from './components/pages/ReceiptEntryPage';
import TransactionsPage from './components/pages/TransactionsPage';
import BudgetPage from './components/pages/BudgetPage';
import ReportsPage from './components/pages/ReportsPage';
import ForecastAlertsPage from './components/pages/ForecastAlertsPage';
import { DEFAULT_TRANSACTIONS, DEFAULT_BUDGETS, DEFAULT_ALERTS, TRANSLATIONS } from './data';
import { Transaction, Budgets, Alert } from './types';

export default function App() {
  const [activeTab, setActiveTab] = useState<string>('dashboard');
  const [lang, setLang] = useState<'en' | 'bm'>('en');

  // Core st.session_state structures in local state
  const [transactions, setTransactions] = useState<Transaction[]>(DEFAULT_TRANSACTIONS);
  const [budgets, setBudgets] = useState<Budgets>(DEFAULT_BUDGETS);
  const [alerts, setAlerts] = useState<Alert[]>(DEFAULT_ALERTS);

  const t = TRANSLATIONS[lang];

  // Callback: Add manual/OCR transactions with dynamic overspend warning calculation!
  const handleAddTransaction = (newTx: Omit<Transaction, 'id'>) => {
    const uid = String(Date.now());
    const txObj: Transaction = {
      ...newTx,
      id: uid,
    };

    setTransactions((prev) => [txObj, ...prev]);

    // Calculate total spent for this specific category in June 2025 (current core month)
    const category = newTx.category;
    const spentInCat = transactions
      .filter((t) => t.date.startsWith('2025-06') && t.category === category)
      .reduce((sum, t) => sum + t.amount, 0) + newTx.amount;

    const limit = budgets[category as keyof Budgets] || 0;

    // Trigger warning alert dynamically
    if (limit > 0 && spentInCat > limit) {
      const isAlreadyWarned = alerts.some(
        (a) => a.category === category && a.type === 'Overspend Warning' && !a.dismissed
      );

      if (!isAlreadyWarned) {
        const newAlert: Alert = {
          id: 'alert_' + Date.now(),
          type: 'Overspend Warning',
          category,
          amount: newTx.amount,
          date: newTx.date,
          severity: 'Medium',
          dismissed: false,
        };
        setAlerts((prev) => [newAlert, ...prev]);
      }
    }
  };

  const handleUpdateTransaction = (id: string, updatedFields: Partial<Transaction>) => {
    setTransactions((prev) =>
      prev.map((t) => (t.id === id ? { ...t, ...updatedFields } : t))
    );
  };

  const handleDeleteTransactions = (ids: string[]) => {
    setTransactions((prev) => prev.filter((t) => !ids.includes(t.id)));
  };

  const handleUpdateBudgets = (newBudgets: Budgets) => {
    setBudgets(newBudgets);
  };

  const handleDismissAlert = (id: string) => {
    setAlerts((prev) =>
      prev.map((a) => (a.id === id ? { ...a, dismissed: true } : a))
    );
  };

  // Switch Render page panel
  const renderActivePage = () => {
    switch (activeTab) {
      case 'dashboard':
        return (
          <DashboardPage
            transactions={transactions}
            budgets={budgets}
            alerts={alerts}
            setActiveTab={setActiveTab}
            t={t}
          />
        );
      case 'receipt_entry':
        return <ReceiptEntryPage onAddTransaction={handleAddTransaction} t={t} />;
      case 'transactions':
        return (
          <TransactionsPage
            transactions={transactions}
            onUpdateTransaction={handleUpdateTransaction}
            onDeleteTransactions={handleDeleteTransactions}
            t={t}
          />
        );
      case 'budget':
        return (
          <BudgetPage
            transactions={transactions}
            budgets={budgets}
            onUpdateBudgets={handleUpdateBudgets}
            t={t}
          />
        );
      case 'reports':
        return <ReportsPage transactions={transactions} t={t} />;
      case 'forecast_alerts':
        return (
          <ForecastAlertsPage
            alerts={alerts}
            transactions={transactions}
            budgets={budgets}
            onDismissAlert={handleDismissAlert}
            setActiveTab={setActiveTab}
            t={t}
          />
        );
      default:
        return (
          <DashboardPage
            transactions={transactions}
            budgets={budgets}
            alerts={alerts}
            setActiveTab={setActiveTab}
            t={t}
          />
        );
    }
  };

  return (
    <div className="min-h-screen bg-[#fcfdfd] flex">
      {/* 1. Permanent side layout panel */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        lang={lang}
        setLang={setLang}
        t={t}
      />

      {/* 2. Scrollable center main panel content */}
      <main className="flex-1 ml-80 p-8 max-w-7xl mx-auto min-h-screen">
        <div className="bg-white/80 backdrop-blur-md rounded-2xl border border-[#e0f1ee]/40 p-6 sm:p-8 min-h-[calc(100vh-4rem)] shadow-lg shadow-[#0f7b6c]/3">
          {renderActivePage()}
        </div>
      </main>
    </div>
  );
}
