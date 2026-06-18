export interface Transaction {
  id: string;
  merchant: string;
  amount: number;
  date: string; // YYYY-MM-DD
  category: string;
  notes: string;
  source: 'ocr' | 'manual';
}

export type Category = 'Food & Dining' | 'Transport' | 'Shopping' | 'Bills' | 'Entertainment' | 'Other';

export interface Budgets {
  'Food & Dining': number;
  'Transport': number;
  'Shopping': number;
  'Bills': number;
  'Entertainment': number;
  'Other': number;
}

export interface Alert {
  id: string;
  type: 'Unusual Spike' | 'Overspend Warning' | 'Duplicate Transaction';
  category: string;
  amount: number;
  date: string;
  severity: 'High' | 'Medium';
  dismissed: boolean;
}

export interface ForecastResponse {
  projected_total: number;
  by_category: { [category: string]: number };
  confidence: 'High' | 'Medium' | 'Low';
  tip: string;
}

export interface TranslationSet {
  dashboard: string;
  receiptEntry: string;
  transactions: string;
  budgets: string;
  reports: string;
  forecastAlerts: string;
  logoSubtitle: string;
  userId: string;
  langToggle: string;
  totalSpentThisMonth: string;
  budgetRemaining: string;
  txThisWeek: string;
  activeAlerts: string;
  spendingByCategory: string;
  budgetVsActual: string;
  recentTransactions: string;
  viewAll: string;
  uploadReceipt: string;
  ocrTab: string;
  manualTab: string;
  uploadReceiptLabel: string;
  cameraInputLabel: string;
  extractingSpinner: string;
  ocrResult: string;
  merchantName: string;
  amountLabel: string;
  dateLabel: string;
  categoryLabel: string;
  saveTransaction: string;
  confirmSave: string;
  notesLabel: string;
  successAdded: string;
  filters: string;
  applyFilters: string;
  deleteSelected: string;
  manageCategories: string;
  categoryName: string;
  budgetLimit: string;
  amountSpent: string;
  remaining: string;
  saveAllBudgets: string;
  currentMonth: string;
  history: string;
  totalSpent: string;
  highestCategory: string;
  mostFrequentMerchant: string;
  avgDailySpend: string;
  dailySpendingTrend: string;
  totalSpentCategory: string;
  percentBreakdown: string;
  downloadCsv: string;
  noAlertsDetected: string;
  anomalyAlerts: string;
  dismiss: string;
  reviewTx: string;
  aiForecast: string;
  refreshForecast: string;
  confidenceCaption: string;
  projectedSpend: string;
  onTrack: string;
  atRisk: string;
  overBudget: string;
}
