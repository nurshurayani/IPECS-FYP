DEFAULT_TRANSACTIONS = [
  {"id": "1", "merchant": "Restoran Ali Maju", "amount": 12.50, "date": "2025-06-01", "category": "Food & Dining", "notes": "Dinner with friends", "source": "manual"},
  {"id": "2", "merchant": "MyRapid Bus", "amount": 2.10, "date": "2025-06-02", "category": "Transport", "notes": "Bus fare to campus", "source": "manual"},
  {"id": "3", "merchant": "Lotus's Ara Damansara", "amount": 67.80, "date": "2025-06-03", "category": "Shopping", "notes": "Monthly groceries", "source": "manual"},
  {"id": "4", "merchant": "Unifi Monthly", "amount": 89.00, "date": "2025-06-05", "category": "Bills", "notes": "Broadband subscription", "source": "manual"},
  {"id": "5", "merchant": "TGV Cinemas", "amount": 23.00, "date": "2025-06-07", "category": "Entertainment", "notes": "Movie night", "source": "manual"},
  {"id": "6", "merchant": "KFC Mid Valley", "amount": 25.90, "date": "2025-06-08", "category": "Food & Dining", "notes": "Lunch snack", "source": "ocr"},
  {"id": "7", "merchant": "Grab Ride", "amount": 15.00, "date": "2025-06-10", "category": "Transport", "notes": "Ride to clinic", "source": "manual"},
  {"id": "8", "merchant": "Popular Bookstore", "amount": 45.00, "date": "2025-06-11", "category": "Shopping", "notes": "Reference books for exam", "source": "ocr"},
  {"id": "9", "merchant": "Tenaga Nasional", "amount": 110.00, "date": "2025-06-12", "category": "Bills", "notes": "Electricity bill share", "source": "manual"},
  {"id": "10", "merchant": "FamilyMart UM", "amount": 14.20, "date": "2025-06-14", "category": "Food & Dining", "notes": "Oden snack", "source": "ocr"},
  {"id": "11", "merchant": "Tealive", "amount": 9.50, "date": "2025-06-15", "category": "Food & Dining", "notes": "Boba milk tea", "source": "manual"},
  {"id": "12", "merchant": "Decathlon MY", "amount": 85.00, "date": "2025-06-15", "category": "Shopping", "notes": "Sportswear", "source": "ocr"},
  {"id": "13", "merchant": "RapidKL LRT", "amount": 3.50, "date": "2025-06-16", "category": "Transport", "notes": "LRT to KL Sentral", "source": "manual"},
  {"id": "14", "merchant": "Watson's Pharmacy", "amount": 32.40, "date": "2025-06-17", "category": "Shopping", "notes": "Hygiene products", "source": "manual"},
  {"id": "15", "merchant": "Mamak Ali UM", "amount": 8.00, "date": "2025-06-18", "category": "Food & Dining", "notes": "Roti canai and teh tarik", "source": "manual"}
]

DEFAULT_BUDGETS = {
  "Food & Dining": 300.0,
  "Transport": 100.0,
  "Shopping": 200.0,
  "Bills": 150.0,
  "Entertainment": 100.0,
  "Other": 50.0
}

DEFAULT_ALERTS = [
  {"id": "a1", "type": "Overspend Warning", "category": "Shopping", "amount": 67.80, "date": "2025-06-03", "severity": "Medium", "dismissed": False},
  {"id": "a2", "type": "Unusual Spike", "category": "Entertainment", "amount": 23.00, "date": "2025-06-07", "severity": "High", "dismissed": False},
]
