import { useState, useMemo } from 'react';
import { AlertCircle, Brain, RefreshCw, Sparkles, Check, Info, ShieldAlert } from 'lucide-react';
import { Alert, Transaction, Budgets, ForecastResponse, TranslationSet } from '../../types';

interface ForecastAlertsPageProps {
  alerts: Alert[];
  transactions: Transaction[];
  budgets: Budgets;
  onDismissAlert: (id: string) => void;
  setActiveTab: (tab: string) => void;
  t: TranslationSet;
}

export default function ForecastAlertsPage({
  alerts,
  transactions,
  budgets,
  onDismissAlert,
  setActiveTab,
  t
}: ForecastAlertsPageProps) {
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [forecast, setForecast] = useState<ForecastResponse | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [loadingStep, setLoadingStep] = useState(0);

  const activeAlerts = useMemo(() => {
    return alerts.filter((a) => !a.dismissed);
  }, [alerts]);

  // Loading steps to show assuring messages as requested in system rules
  const loadingMessages = [
    "Compiling past 90 days transaction logs...",
    "Scanning budget envelopes per category...",
    "Querying Gemini 3.5 AI model for budget regression...",
    "Generating custom Malaysian student saving tip..."
  ];

  const handleRefreshForecast = async () => {
    setIsRefreshing(true);
    setForecast(null);
    setErrorMsg(null);
    setLoadingStep(0);

    // Dynamic step messages
    const stepInterval = setInterval(() => {
      setLoadingStep((prev) => (prev < loadingMessages.length - 1 ? prev + 1 : prev));
    }, 1200);

    try {
      const response = await fetch('/api/forecast', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ transactions, budgets }),
      });

      let result: any = null;
      try {
        result = await response.json();
      } catch (jsonErr) {
        // Response content is not JSON (e.g. gateway timeout or crash HTML)
      }

      if (result && result.error) {
        throw new Error(result.error);
      }

      if (!response.ok) {
        throw new Error('Failed to reach AI server. Make sure GEMINI_API_KEY is active.');
      }

      setForecast(result);
    } catch (err: any) {
      console.error(err);
      setErrorMsg(err.message || 'Error occurred querying the Gemini forecast endpoint.');
    } finally {
      clearInterval(stepInterval);
      setIsRefreshing(false);
    }
  };

  return (
    <div className="space-y-8 animate-fade-in text-xs text-gray-700">
      
      {/* Title */}
      <div className="border-b border-[#e0f1ee] pb-4">
        <h2 className="text-2xl font-bold text-gray-800 font-sans tracking-tight flex items-center gap-2">
          <span>{t.forecastAlerts.split(' ')[0]}</span>
          <span>{t.forecastAlerts.replace(/^[^\w\s]+/g, '').trim()}</span>
        </h2>
        <p className="text-sm text-gray-500 font-mono">
          Detect transaction spikes instantly and consult Gemini AI on smart budget caps.
        </p>
      </div>

      {/* 1. Anomaly Alerts section */}
      <div className="space-y-4">
        <h3 className="text-base font-bold text-gray-800 flex items-center gap-2">
          <ShieldAlert className="h-5 w-5 text-[#0F7B6C]" />
          <span>{t.anomalyAlerts}</span>
        </h3>

        {activeAlerts.length === 0 ? (
          <div className="bg-[#f0fdfa] border border-[#cbd5e1] rounded-xl p-5 text-center text-sm font-semibold text-[#0a5c51] leading-relaxed">
            {t.noAlertsDetected}
          </div>
        ) : (
          <div className="space-y-3">
            {activeAlerts.map((alert) => {
              const IsHigh = alert.severity === 'High';
              return (
                <div
                  key={alert.id}
                  className={`border-2 rounded-xl p-4 flex flex-col md:flex-row justify-between items-start md:items-center gap-4 transition-all shadow-sm ${
                    IsHigh ? 'bg-red-50/50 border-red-200' : 'bg-amber-50/50 border-amber-200'
                  }`}
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase ${
                          IsHigh ? 'bg-red-500 text-white' : 'bg-amber-500 text-white'
                        }`}
                      >
                        {alert.severity} SEVERITY
                      </span>
                      <span className="text-[11px] font-mono font-semibold text-gray-500">{alert.date}</span>
                    </div>

                    <h4 className="text-sm font-bold text-gray-800">
                      {alert.type}: Spent <span className="font-mono text-red-600">RM {alert.amount.toFixed(2)}</span> on{' '}
                      <span className="font-semibold text-[#0F7B6C]">{alert.category}</span>
                    </h4>
                    <p className="text-xs text-gray-500">
                      Anomaly trigger: Unusual spending behavior detected in {alert.category} compared to Mamak caps.
                    </p>
                  </div>

                  <div className="flex gap-2 shrink-0">
                    <button
                      onClick={() => onDismissAlert(alert.id)}
                      className="px-3 py-1.5 bg-white border border-gray-300 hover:bg-gray-100 rounded-lg font-bold font-mono text-[10px] text-gray-700 transition"
                    >
                      {t.dismiss}
                    </button>
                    <button
                      onClick={() => setActiveTab('transactions')}
                      className="px-3 py-1.5 bg-[#0F7B6C] hover:bg-[#0a5c51] rounded-lg font-bold font-mono text-[10px] text-white transition flex items-center gap-1 shadow-sm"
                    >
                      <span>{t.reviewTx}</span>
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* 2. Spending Forecast section */}
      <div className="space-y-4 border-t border-[#e0f1ee] pt-6">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div className="space-y-1">
            <h3 className="text-base font-bold text-gray-800 flex items-center gap-2">
              <Brain className="h-5 w-5 text-[#0F7B6C]" />
              <span>{t.aiForecast}</span>
            </h3>
            <p className="text-xs text-gray-500 font-mono">{t.confidenceCaption}</p>
          </div>

          <button
            onClick={handleRefreshForecast}
            disabled={isRefreshing}
            className="flex items-center gap-1.5 bg-[#0F7B6C] hover:bg-[#0a5c51] text-white px-5 py-2.5 rounded-lg text-xs font-bold font-mono uppercase tracking-wider shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${isRefreshing ? 'animate-spin' : ''}`} />
            <span>{t.refreshForecast}</span>
          </button>
        </div>

        {/* Loading state spinner with Assurance Messages */}
        {isRefreshing && (
          <div className="bg-white border-2 border-dashed border-[#b4e2da] rounded-xl p-8 text-center flex flex-col items-center justify-center space-y-4 shadow-sm animate-pulse">
            <div className="w-12 h-12 rounded-full border-t-2 border-b-2 border-[#0F7B6C] animate-spin" />
            <div className="space-y-1">
              <h4 className="text-sm font-bold text-[#0F7B6C]">Running Forecast Calculations</h4>
              <p className="text-xs font-mono text-gray-500">{loadingMessages[loadingStep]}</p>
            </div>
          </div>
        )}

        {/* Error State */}
        {errorMsg && (
          <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-xl flex items-start gap-2.5">
            <AlertCircle className="h-5 w-5 shrink-0 text-red-500" />
            <div className="text-xs">
              <h5 className="font-bold mb-1">Gemini Forecast Error</h5>
              <p className="font-mono leading-relaxed">{errorMsg}</p>
              <p className="mt-1">
                Make sure your `GEMINI_API_KEY` is configured correctly in the **Settings &gt; Secrets** panel.
              </p>
            </div>
          </div>
        )}

        {/* Forecast Output Area */}
        {forecast && (
          <div className="bg-white border border-[#e0f1ee] rounded-xl p-6 shadow-sm space-y-6 animate-fade-in">
            <div className="flex justify-between items-center border-b border-gray-100 pb-4">
              <div>
                <span className="text-[10px] font-mono text-gray-400 font-bold block uppercase">PROJECTED 30-DAY OUTLOOK</span>
                <div className="flex items-baseline gap-1 mt-1">
                  <span className="text-xs font-bold text-[#0F7B6C]">RM</span>
                  <span className="text-2xl font-bold font-mono text-gray-800">
                    {forecast.projected_total.toFixed(2)}
                  </span>
                </div>
              </div>

              <div className="text-right">
                <span className="text-[10px] font-mono text-gray-400 block uppercase font-bold">MODEL CONFIDENCE</span>
                <span className="inline-block mt-1 bg-[#10B981]/10 text-[#10B981] border border-[#10B981]/20 font-bold text-[10px] font-mono px-2.5 py-0.5 rounded-full uppercase">
                  {forecast.confidence}
                </span>
              </div>
            </div>

            {/* Custom metrics cards per category projection */}
            <div className="space-y-3">
              <h4 className="text-xs font-mono font-bold text-gray-400 uppercase tracking-wider">
                BY-CATEGORY 30-DAY FORECASTS
              </h4>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3">
                {Object.entries(forecast.by_category).map(([cat, projection]) => {
                  const budgetVal = budgets[cat as keyof Budgets] || 0;
                  const proj = Number(projection) || 0;
                  const isOver = budgetVal > 0 && proj > budgetVal;
                  return (
                    <div key={cat} className="p-3 border border-gray-100 rounded-lg bg-gray-50/50 flex flex-col justify-between">
                      <span className="font-semibold text-gray-600 truncate">{cat}</span>
                      <div className="mt-2">
                        <span className="text-[10px] text-gray-400 font-mono">RM </span>
                        <span className="font-bold text-sm font-mono text-gray-800">{proj.toFixed(0)}</span>
                      </div>
                      {budgetVal > 0 && (
                        <span className={`text-[9px] font-mono font-bold mt-1 block ${isOver ? 'text-red-500' : 'text-green-600'}`}>
                          {isOver ? `⚠️ limit ${budgetVal}` : `✅ caps ${budgetVal}`}
                        </span>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>

            {/* AI Custom Tip block - manglish English */}
            <div className="bg-[#eff6ff] border-2 border-blue-200 rounded-xl p-5 flex items-start gap-4">
              <div className="p-2 bg-[#2563eb] text-white rounded-lg block self-center">
                <Sparkles className="h-5 w-5" />
              </div>
              <div>
                <h5 className="font-bold text-blue-900 text-sm mb-1">Gemini AI Saving Recommendation</h5>
                <p className="text-xs text-gray-600 leading-relaxed font-semibold italic">
                  "{forecast.tip}"
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Informative placeholder cards before they run first scan */}
        {!forecast && !isRefreshing && !errorMsg && (
          <div className="bg-[#f8fffe] border border-[#e0f1ee] rounded-xl p-6 text-center space-y-4">
            <div className="w-12 h-12 bg-[#0F7B6C]/10 text-[#0F7B6C] rounded-full flex items-center justify-center mx-auto">
              <Brain className="h-6 w-6 animate-pulse" />
            </div>
            <div className="max-w-md mx-auto space-y-1">
              <h4 className="text-sm font-bold text-gray-700">Unlock your AI-driven financial outlook</h4>
              <p className="text-xs text-gray-400 leading-normal">
                Click **Refresh Forecast** button to let Gemini digest your exact categories, budgets, and last 15 June transactions to create a strict projection for next 30 days. Fits study budgets perfectly!
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
