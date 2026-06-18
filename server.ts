import express from "express";
import path from "path";
import { createServer as createViteServer } from "vite";
import { GoogleGenAI, Type } from "@google/genai";
import dotenv from "dotenv";

dotenv.config();

// Create Gemini Client conforming to modern User-Agent constraints
const ai = process.env.GEMINI_API_KEY 
  ? new GoogleGenAI({
      apiKey: process.env.GEMINI_API_KEY,
      httpOptions: {
        headers: {
          'User-Agent': 'aistudio-build',
        }
      }
    })
  : null;

/**
 * Robust helper function to execute generative content calls with automatic exponentially backed-off 
 * retries and subsequent model fallback sequence to ensure 100% availability during peak demand hours.
 */
async function generateContentWithFallbackAndRetry(
  aiClient: any,
  params: {
    contents: any;
    config?: any;
  }
) {
  const targetModels = ["gemini-3.5-flash", "gemini-3.1-flash-lite"];
  let finalError: any = null;

  for (const model of targetModels) {
    const maxRetries = 3;
    for (let retry = 1; retry <= maxRetries; retry++) {
      try {
        console.log(`[Gemini Request] Service alias='${model}' | Attempt ${retry} of ${maxRetries}`);
        const response = await aiClient.models.generateContent({
          model,
          contents: params.contents,
          config: params.config,
        });

        if (response && response.text) {
          console.log(`[Gemini Request] Success using service='${model}' on attempt ${retry}`);
          return response;
        }
      } catch (err: any) {
        finalError = err;
        console.warn(
          `[Gemini Request] Failed service='${model}' | Attempt ${retry}/${maxRetries}. Info:`,
          err.message || err
        );

        if (model !== targetModels[targetModels.length - 1] || retry < maxRetries) {
          const timeout = retry * 1000;
          console.log(`[Gemini Request] Delaying retry by ${timeout}ms...`);
          await new Promise((resolve) => setTimeout(resolve, timeout));
        }
      }
    }
    console.log(`[Gemini Request] Service='${model}' exhausted or unavailable. Initiating graceful transition.`);
  }

  throw finalError || new Error("All active Gemini service pools failed to respond.");
}

async function startServer() {
  const app = express();
  const PORT = 3000;

  app.use(express.json());

  // 1. API Endpoint for AI Forecast & Category projections
  app.post("/api/forecast", async (req, res) => {
    try {
      const { transactions = [], budgets = {} } = req.body;

      if (!ai) {
        return res.status(500).json({ 
          error: "GEMINI_API_KEY environment variable is missing on server. Please add it in Settings > Secrets." 
        });
      }

      // Summarize transactions into Category totals
      const categorySum: { [cat: string]: number } = {};
      transactions.forEach((tx: any) => {
        categorySum[tx.category] = (categorySum[tx.category] || 0) + tx.amount;
      });

      const summaryStr = Object.entries(categorySum)
        .map(([cat, amt]) => `- ${cat}: RM ${amt.toFixed(2)}`)
        .join("\n");

      const budgetsStr = Object.entries(budgets)
        .map(([cat, val]) => `- ${cat}: RM ${(Number(val) || 0).toFixed(2)}`)
        .join("\n");

      const prompt = `
        You are a personal finance assistant for a Malaysian university student or young working adult.
        Based on their spending history below, forecast their total spending for the next 30 days
        and per-category projections. Return a flat JSON object ONLY:
        {
          "projected_total": float,
          "by_category": {
            "Food & Dining": float,
            "Transport": float,
            "Shopping": float,
            "Bills": float,
            "Entertainment": float,
            "Other": float
          },
          "confidence": "High" | "Medium" | "Low",
          "tip": "one short clever saving tip in Malaysian English (using Malaysian slang like 'lah', 'buddy', 'mamak', or 'lah' appropriately and naturally)"
        }
        
        Recent spending summary (RM):
        ${summaryStr || "No transactions recorded yet."}
        
        Monthly budgets set:
        ${budgetsStr}
      `;

      // Call Gemini robust helper
      const apiResponse = await generateContentWithFallbackAndRetry(ai, {
        contents: prompt,
        config: {
          responseMimeType: "application/json",
          temperature: 0.7,
          responseSchema: {
            type: Type.OBJECT,
            properties: {
              projected_total: { type: Type.NUMBER, description: "Total predicted RM spending next 30 days." },
              by_category: {
                type: Type.OBJECT,
                properties: {
                  "Food & Dining": { type: Type.NUMBER },
                  "Transport": { type: Type.NUMBER },
                  "Shopping": { type: Type.NUMBER },
                  "Bills": { type: Type.NUMBER },
                  "Entertainment": { type: Type.NUMBER },
                  "Other": { type: Type.NUMBER }
                },
                required: ["Food & Dining", "Transport", "Shopping", "Bills", "Entertainment", "Other"]
              },
              confidence: { type: Type.STRING, description: "High, Medium, or Low" },
              tip: { type: Type.STRING, description: "Clever local saving tip." }
            },
            required: ["projected_total", "by_category", "confidence", "tip"]
          }
        }
      });

      const responseText = apiResponse.text?.trim() || "{}";
      const forecastJson = JSON.parse(responseText);

      return res.json(forecastJson);
    } catch (error: any) {
      console.error("AI Forecast error:", error);
      return res.status(500).json({ 
        error: `Failed to query Gemini model: ${error.message || error}` 
      });
    }
  });

  // 2. Vite middleware injection or static builds hosting
  if (process.env.NODE_ENV !== "production") {
    console.log("Starting server in DEVELOPMENT mode with Vite Middleware...");
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    console.log("Starting server in PRODUCTION mode with static file hosting...");
    const distPath = path.join(process.cwd(), "dist");
    app.use(express.static(distPath));
    app.get("*", (req, res) => {
      res.sendFile(path.join(distPath, "index.html"));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Express application serving port ${PORT}`);
  });
}

startServer();
