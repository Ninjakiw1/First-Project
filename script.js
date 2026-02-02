const STORAGE_KEY = "finance-tracker-transactions";

const form = document.getElementById("transactionForm");
const list = document.getElementById("transactionList");
const categoryStats = document.getElementById("categoryStats");
const accountStats = document.getElementById("accountStats");
const balanceValue = document.getElementById("balanceValue");
const incomeValue = document.getElementById("incomeValue");
const expenseValue = document.getElementById("expenseValue");
const recurringValue = document.getElementById("recurringValue");
const searchInput = document.getElementById("searchInput");
const typeFilter = document.getElementById("typeFilter");
const categoryFilter = document.getElementById("categoryFilter");
const noTransactionsHint = document.getElementById("noTransactionsHint");
const seedDemoButton = document.getElementById("seedDemo");
const clearAllButton = document.getElementById("clearAll");

const template = document.getElementById("transactionItemTemplate");

const formatCurrency = (value) =>
  new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(
    value
  );

const formatDate = (dateString) =>
  new Date(dateString).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });

const loadTransactions = () => {
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) {
    return [];
  }
  try {
    return JSON.parse(raw);
  } catch (error) {
    console.error("Failed to parse stored transactions", error);
    return [];
  }
};

const saveTransactions = (transactions) => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(transactions));
};

let transactions = loadTransactions();

const updateCategoryFilter = () => {
  const categories = [
    ...new Set(transactions.map((transaction) => transaction.category)),
  ];
  categoryFilter.innerHTML = '<option value="all">All categories</option>';
  categories.forEach((category) => {
    const option = document.createElement("option");
    option.value = category;
    option.textContent = category;
    categoryFilter.append(option);
  });
};

const renderStats = (filteredTransactions) => {
  const income = filteredTransactions
    .filter((transaction) => transaction.type === "income")
    .reduce((sum, transaction) => sum + transaction.amount, 0);
  const expenses = filteredTransactions
    .filter((transaction) => transaction.type === "expense")
    .reduce((sum, transaction) => sum + transaction.amount, 0);
  const recurring = filteredTransactions
    .filter((transaction) => transaction.recurring)
    .reduce((sum, transaction) => sum + transaction.amount, 0);

  balanceValue.textContent = formatCurrency(income - expenses);
  incomeValue.textContent = formatCurrency(income);
  expenseValue.textContent = formatCurrency(expenses);
  recurringValue.textContent = formatCurrency(recurring);

  const categoryTotals = filteredTransactions
    .filter((transaction) => transaction.type === "expense")
    .reduce((acc, transaction) => {
      acc[transaction.category] = (acc[transaction.category] || 0) +
        transaction.amount;
      return acc;
    }, {});

  const accountTotals = filteredTransactions.reduce((acc, transaction) => {
    const multiplier = transaction.type === "income" ? 1 : -1;
    acc[transaction.account] = (acc[transaction.account] || 0) +
      transaction.amount * multiplier;
    return acc;
  }, {});

  categoryStats.innerHTML = "";
  if (Object.keys(categoryTotals).length === 0) {
    categoryStats.innerHTML = "<p class=\"hint\">No expense data yet.</p>";
  } else {
    Object.entries(categoryTotals)
      .sort(([, a], [, b]) => b - a)
      .forEach(([category, total]) => {
        const item = document.createElement("div");
        item.className = "stat-item";
        item.innerHTML = `<span>${category}</span><span>${formatCurrency(
          total
        )}</span>`;
        categoryStats.append(item);
      });
  }

  accountStats.innerHTML = "";
  if (Object.keys(accountTotals).length === 0) {
    accountStats.innerHTML = "<p class=\"hint\">No accounts tracked yet.</p>";
  } else {
    Object.entries(accountTotals)
      .sort(([, a], [, b]) => b - a)
      .forEach(([account, total]) => {
        const item = document.createElement("div");
        item.className = "stat-item";
        item.innerHTML = `<span>${account}</span><span>${formatCurrency(
          total
        )}</span>`;
        accountStats.append(item);
      });
  }

  noTransactionsHint.style.display = filteredTransactions.length ? "none" : "";
};

const renderTransactions = () => {
  const searchValue = searchInput.value.toLowerCase();
  const typeValue = typeFilter.value;
  const categoryValue = categoryFilter.value;

  const filtered = transactions.filter((transaction) => {
    const matchesSearch =
      transaction.description.toLowerCase().includes(searchValue) ||
      transaction.notes.toLowerCase().includes(searchValue);
    const matchesType = typeValue === "all" || transaction.type === typeValue;
    const matchesCategory =
      categoryValue === "all" || transaction.category === categoryValue;

    return matchesSearch && matchesType && matchesCategory;
  });

  list.innerHTML = "";
  if (filtered.length === 0) {
    list.innerHTML = "<p class=\"hint\">No transactions match these filters.</p>";
  } else {
    filtered
      .sort((a, b) => new Date(b.date) - new Date(a.date))
      .forEach((transaction) => {
        const node = template.content.cloneNode(true);
        const title = node.querySelector(".item-title");
        const subtitle = node.querySelector(".item-subtitle");
        const tag = node.querySelector(".item-tag");
        const amount = node.querySelector(".item-amount");

        title.textContent = transaction.description;
        subtitle.textContent = `${transaction.account} • ${formatDate(
          transaction.date
        )} • ${transaction.recurring ? "Recurring" : "One-time"}`;
        tag.textContent = transaction.category;
        amount.textContent = formatCurrency(
          transaction.type === "expense"
            ? -transaction.amount
            : transaction.amount
        );
        amount.className = transaction.type === "expense"
          ? "item-amount negative"
          : "item-amount positive";

        list.append(node);
      });
  }

  renderStats(filtered);
};

const addTransaction = (data) => {
  transactions.push(data);
  saveTransactions(transactions);
  updateCategoryFilter();
  renderTransactions();
};

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const formData = new FormData(form);

  const transaction = {
    id: crypto.randomUUID(),
    description: formData.get("description"),
    amount: Math.abs(Number(formData.get("amount"))),
    type: formData.get("type"),
    category: formData.get("category"),
    account: formData.get("account"),
    date: formData.get("date"),
    recurring: formData.get("recurring") === "on",
    notes: formData.get("notes") || "",
  };

  addTransaction(transaction);
  form.reset();
});

[searchInput, typeFilter, categoryFilter].forEach((element) => {
  element.addEventListener("input", renderTransactions);
  element.addEventListener("change", renderTransactions);
});

seedDemoButton.addEventListener("click", () => {
  const sample = [
    {
      id: crypto.randomUUID(),
      description: "Monthly paycheck",
      amount: 4200,
      type: "income",
      category: "Income",
      account: "Checking",
      date: "2024-03-01",
      recurring: true,
      notes: "Employer direct deposit",
    },
    {
      id: crypto.randomUUID(),
      description: "Rent payment",
      amount: 1650,
      type: "expense",
      category: "Bills",
      account: "Checking",
      date: "2024-03-03",
      recurring: true,
      notes: "Autopay",
    },
    {
      id: crypto.randomUUID(),
      description: "Grocery store",
      amount: 184.32,
      type: "expense",
      category: "Groceries",
      account: "Visa",
      date: "2024-03-05",
      recurring: false,
      notes: "Weekly stock-up",
    },
    {
      id: crypto.randomUUID(),
      description: "Streaming bundle",
      amount: 24.99,
      type: "expense",
      category: "Subscriptions",
      account: "Visa",
      date: "2024-03-06",
      recurring: true,
      notes: "Entertainment",
    },
    {
      id: crypto.randomUUID(),
      description: "In-app game purchase",
      amount: 6.99,
      type: "expense",
      category: "Entertainment",
      account: "PayPal",
      date: "2024-03-07",
      recurring: false,
      notes: "New skin",
    },
  ];

  transactions = sample;
  saveTransactions(transactions);
  updateCategoryFilter();
  renderTransactions();
});

clearAllButton.addEventListener("click", () => {
  transactions = [];
  saveTransactions(transactions);
  updateCategoryFilter();
  renderTransactions();
});

const initializeForm = () => {
  form.elements.date.valueAsDate = new Date();
  updateCategoryFilter();
  renderTransactions();
};

initializeForm();
