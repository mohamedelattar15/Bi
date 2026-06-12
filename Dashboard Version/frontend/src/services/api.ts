/**
 * API client for the Grocery Sales Dashboard backend.
 * All requests go through this module for centralized error handling.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function fetchApi<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const response = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const errorBody = await response.text().catch(() => "");
    throw new ApiError(
      `API Error ${response.status}: ${errorBody || response.statusText}`,
      response.status
    );
  }

  return response.json();
}

// ==========================================
// Dashboard API
// ==========================================

export interface DashboardParams {
  start_date?: string;
  end_date?: string;
}

export interface ChartFilterParams extends DashboardParams {
  category?: string;
  product?: string;
}

function buildSearchParams(params?: DashboardParams | ChartFilterParams): string {
  if (!params) return "";
  const sp = new URLSearchParams();
  if ("start_date" in params && params.start_date) sp.set("start_date", params.start_date);
  if ("end_date" in params && params.end_date) sp.set("end_date", params.end_date);
  if ("category" in params && (params as ChartFilterParams).category) sp.set("category", (params as ChartFilterParams).category!);
  if ("product" in params && (params as ChartFilterParams).product) sp.set("product", (params as ChartFilterParams).product!);
  const qs = sp.toString();
  return qs ? `?${qs}` : "";
}

export const dashboardApi = {
  getSummary: (params?: DashboardParams) =>
    fetchApi<any>(`/api/dashboard/summary${buildSearchParams(params)}`),
};

// ==========================================
// Sales API
// ==========================================

export const salesApi = {
  getOverTime: (params?: ChartFilterParams) =>
    fetchApi<any[]>(`/api/sales/over-time${buildSearchParams(params)}`),
  getByCategory: (params?: ChartFilterParams) =>
    fetchApi<any[]>(`/api/sales/by-category${buildSearchParams(params)}`),
  getMonthly: (params?: ChartFilterParams) =>
    fetchApi<any[]>(`/api/sales/monthly${buildSearchParams(params)}`),
  getByCity: (params?: DashboardParams) =>
    fetchApi<any[]>(`/api/sales/by-city${buildSearchParams(params)}`),
  getFunnelByCity: (params?: DashboardParams) =>
    fetchApi<any[]>(`/api/sales/funnel-by-city${buildSearchParams(params)}`),
  getCaGrowthByYear: (params?: DashboardParams) =>
    fetchApi<any[]>(`/api/sales/ca-growth-by-year${buildSearchParams(params)}`),
  getByClass: (params?: DashboardParams) =>
    fetchApi<any[]>(`/api/sales/by-class${buildSearchParams(params)}`),
};

// ==========================================
// Products API
// ==========================================

function buildDateParams(params?: DashboardParams, hasExistingParams = false): string {
  if (!params) return "";
  const sp = new URLSearchParams();
  if (params.start_date) sp.set("start_date", params.start_date);
  if (params.end_date) sp.set("end_date", params.end_date);
  const qs = sp.toString();
  if (!qs) return "";
  return hasExistingParams ? `&${qs}` : `?${qs}`;
}

export const productsApi = {
  getAll: (params?: DashboardParams) =>
    fetchApi<any[]>(`/api/products/${buildDateParams(params)}`),
  getById: (id: number) => fetchApi<any>(`/api/products/${id}`),
  getPriceDistribution: (params?: DashboardParams) =>
    fetchApi<any[]>(`/api/products/analytics/price-distribution${buildDateParams(params)}`),
  getPriceVolumeMatrix: (params?: DashboardParams) =>
    fetchApi<any[]>(`/api/products/analytics/price-volume-matrix${buildDateParams(params)}`),
  getAllergenDistribution: () =>
    fetchApi<any[]>("/api/products/analytics/allergen-distribution"),
  getResistanceDistribution: () =>
    fetchApi<any[]>("/api/products/analytics/resistance-distribution"),
  getCategoryGrowth: (params?: DashboardParams) =>
    fetchApi<any[]>(`/api/products/analytics/category-growth${buildDateParams(params)}`),
  getQuantitySummary: (params?: DashboardParams) =>
    fetchApi<any[]>(`/api/products/analytics/quantity-summary${buildDateParams(params)}`),
};

// ==========================================
// Customers API
// ==========================================

export const customersApi = {
  getSegments: () => fetchApi<any[]>("/api/customers/segments"),
  getTop: (limit = 10) => fetchApi<any[]>(`/api/customers/top?limit=${limit}`),
  getActivity: (params?: DashboardParams) => {
    const searchParams = new URLSearchParams();
    if (params?.start_date) searchParams.set("start_date", params.start_date);
    if (params?.end_date) searchParams.set("end_date", params.end_date);
    const query = searchParams.toString();
    return fetchApi<any[]>(
      `/api/customers/activity${query ? `?${query}` : ""}`
    );
  },
  getByTransactions: (limit = 10, params?: DashboardParams) => {
    const searchParams = new URLSearchParams();
    searchParams.set("limit", String(limit));
    if (params?.start_date) searchParams.set("start_date", params.start_date);
    if (params?.end_date) searchParams.set("end_date", params.end_date);
    return fetchApi<any[]>(`/api/customers/by-transactions?${searchParams.toString()}`);
  },
  getAvgBasketByCity: (params?: DashboardParams) =>
    fetchApi<any[]>(`/api/customers/avg-basket-by-city${buildDateParams(params)}`),
  getGrowthByCity: (params?: DashboardParams) =>
    fetchApi<any[]>(`/api/customers/growth-by-city${buildDateParams(params)}`),
  getLoyaltyStats: (params?: DashboardParams) =>
    fetchApi<any>(`/api/customers/loyalty-stats${buildDateParams(params)}`),
  getById: (id: number) => fetchApi<any>(`/api/customers/${id}`),
};

// ==========================================
// Employees API
// ==========================================

export const employeesApi = {
  getTop: (limit = 5, params?: DashboardParams) =>
    fetchApi<any[]>(`/api/employees/top?limit=${limit}${buildDateParams(params, true)}`),
  getPerformanceByAge: (params?: DashboardParams) =>
    fetchApi<any[]>(`/api/employees/performance/by-age${buildDateParams(params)}`),
  getPerformanceBySeniority: (params?: DashboardParams) =>
    fetchApi<any[]>(`/api/employees/performance/by-seniority${buildDateParams(params)}`),
  getAgeCategoryDistribution: () =>
    fetchApi<any[]>("/api/employees/demographics/age-category"),
  getAgeTrancheDistribution: () =>
    fetchApi<any[]>("/api/employees/demographics/age-tranche"),
  getGenderDistribution: () =>
    fetchApi<any[]>("/api/employees/demographics/gender"),
  getCaByAgeTranche: (params?: DashboardParams) =>
    fetchApi<any[]>(`/api/employees/ca-by-age-tranche${buildDateParams(params)}`),
  getPerformanceTable: (params?: DashboardParams) =>
    fetchApi<any[]>(`/api/employees/performance-table${buildDateParams(params)}`),
  getById: (id: number) => fetchApi<any>(`/api/employees/${id}`),
};

// ==========================================
// Basket Analysis API
// ==========================================

export const basketApi = {
  getAnalysis: (minSupport = 0.000001, minLift = 0.0, limit = 50, params?: DashboardParams) =>
    fetchApi<any>(
      `/api/basket/analysis?min_support=${minSupport}&min_lift=${minLift}&limit=${limit}${buildDateParams(params, true)}`
    ),
};

// ==========================================
// Filters API
// ==========================================

export const filtersApi = {
  getOptions: () => fetchApi<any>("/api/filters/"),
};

// ==========================================
// Insights API (advanced charts)
// ==========================================

export const insightsApi = {
  getMonthlyByCategory: (params?: DashboardParams) =>
    fetchApi<any[]>(`/api/insights/monthly-by-category${buildDateParams(params)}`),
  getProfitSummary: (params?: DashboardParams) =>
    fetchApi<any>(`/api/insights/profit-summary${buildDateParams(params)}`),
  getCategoryWaterfall: (params?: DashboardParams) =>
    fetchApi<any[]>(`/api/insights/category-waterfall${buildDateParams(params)}`),
  getParetoProducts: (limit = 20, params?: DashboardParams) => {
    const searchParams = new URLSearchParams();
    searchParams.set("limit", String(limit));
    if (params?.start_date) searchParams.set("start_date", params.start_date);
    if (params?.end_date) searchParams.set("end_date", params.end_date);
    return fetchApi<any[]>(`/api/insights/pareto-products?${searchParams.toString()}`);
  },
  getGrowthMetrics: (params?: DashboardParams) =>
    fetchApi<any>(`/api/insights/growth-metrics${buildDateParams(params)}`),
  getRevenueByDay: () => fetchApi<any[]>("/api/insights/revenue-by-day"),
  getRevenueConcentration: () => fetchApi<any>("/api/insights/revenue-concentration"),
  getMonthOverMonth: () => fetchApi<any[]>("/api/insights/month-over-month"),
  getCustomerRfm: () => fetchApi<any[]>("/api/insights/customer-rfm"),
  getGeographicDistribution: () => fetchApi<any[]>("/api/insights/geographic-distribution"),
  getEmployeeRanking: () => fetchApi<any[]>("/api/insights/employee-ranking"),
};
