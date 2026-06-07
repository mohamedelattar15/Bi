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

export const dashboardApi = {
  getSummary: (params?: DashboardParams) => {
    const searchParams = new URLSearchParams();
    if (params?.start_date) searchParams.set("start_date", params.start_date);
    if (params?.end_date) searchParams.set("end_date", params.end_date);
    const query = searchParams.toString();
    return fetchApi<any>(`/api/dashboard/summary${query ? `?${query}` : ""}`);
  },
};

// ==========================================
// Sales API
// ==========================================

export const salesApi = {
  getOverTime: (params?: DashboardParams) => {
    const searchParams = new URLSearchParams();
    if (params?.start_date) searchParams.set("start_date", params.start_date);
    if (params?.end_date) searchParams.set("end_date", params.end_date);
    const query = searchParams.toString();
    return fetchApi<any[]>(
      `/api/sales/over-time${query ? `?${query}` : ""}`
    );
  },
  getByCategory: (params?: DashboardParams) => {
    const searchParams = new URLSearchParams();
    if (params?.start_date) searchParams.set("start_date", params.start_date);
    if (params?.end_date) searchParams.set("end_date", params.end_date);
    const query = searchParams.toString();
    return fetchApi<any[]>(
      `/api/sales/by-category${query ? `?${query}` : ""}`
    );
  },
  getMonthly: (params?: DashboardParams) => {
    const searchParams = new URLSearchParams();
    if (params?.start_date) searchParams.set("start_date", params.start_date);
    if (params?.end_date) searchParams.set("end_date", params.end_date);
    const query = searchParams.toString();
    return fetchApi<any[]>(
      `/api/sales/monthly${query ? `?${query}` : ""}`
    );
  },
};

// ==========================================
// Products API
// ==========================================

export const productsApi = {
  getAll: () => fetchApi<any[]>("/api/products/"),
  getById: (id: number) => fetchApi<any>(`/api/products/${id}`),
  getPriceDistribution: () =>
    fetchApi<any[]>("/api/products/analytics/price-distribution"),
  getPriceVolumeMatrix: () =>
    fetchApi<any[]>("/api/products/analytics/price-volume-matrix"),
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
  getTop: (limit = 5) =>
    fetchApi<any[]>(`/api/employees/top?limit=${limit}`),
  getPerformanceByAge: () =>
    fetchApi<any[]>("/api/employees/performance/by-age"),
  getPerformanceBySeniority: () =>
    fetchApi<any[]>("/api/employees/performance/by-seniority"),
  getById: (id: number) => fetchApi<any>(`/api/employees/${id}`),
};

// ==========================================
// Basket Analysis API
// ==========================================

export const basketApi = {
  getAnalysis: (minSupport = 0.01, minLift = 1.5, limit = 50) =>
    fetchApi<any>(
      `/api/basket/analysis?min_support=${minSupport}&min_lift=${minLift}&limit=${limit}`
    ),
};

// ==========================================
// Filters API
// ==========================================

export const filtersApi = {
  getOptions: () => fetchApi<any>("/api/filters/"),
};
