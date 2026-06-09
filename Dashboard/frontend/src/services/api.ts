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
  getById: (id: number) => fetchApi<any>(`/api/employees/${id}`),
};

// ==========================================
// Basket Analysis API
// ==========================================

export const basketApi = {
  getAnalysis: (minSupport = 0.01, minLift = 1.5, limit = 50, params?: DashboardParams) =>
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
