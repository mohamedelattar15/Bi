// ==========================================
// Dashboard Types
// ==========================================

export interface KPICard {
  label: string;
  value: number;
  prefix: string;
  suffix: string;
  format: "number" | "currency" | "percentage";
  trend?: number | null;
  trend_direction?: "up" | "down" | "stable" | null;
}

export interface SalesOverTime {
  date: string;
  period: string;
  revenue: number;
  quantity: number;
  transactions: number;
  avg_basket?: number | null;
}

export interface SalesByCategory {
  category: string;
  revenue: number;
  quantity: number;
  percentage?: number | null;
  transaction_count?: number | null;
}

export interface SalesByMonth {
  year: number;
  month: number;
  month_name: string;
  quarter: number;
  revenue: number;
  quantity: number;
  transaction_count: number;
  prev_year_revenue?: number | null;
  yoy_growth?: number | null;
}

export interface TopProduct {
  rank: number;
  product_id: number;
  product_name: string;
  category: string;
  revenue: number;
  quantity_sold: number;
  times_sold: number;
}

export interface DashboardSummary {
  total_revenue: KPICard;
  total_quantity: KPICard;
  total_transactions: KPICard;
  avg_basket: KPICard;
  unique_customers?: KPICard | null;
  total_products?: KPICard | null;
  revenue_over_time: SalesOverTime[];
  sales_by_category: SalesByCategory[];
  monthly_sales: SalesByMonth[];
  top_products: TopProduct[];
  period: string;
  generated_at: string;
}

// ==========================================
// Product Types
// ==========================================

export interface ProductDetail {
  product_id: number;
  product_name: string;
  price: number;
  category: string;
  class_?: string | null;
  resistant?: string | null;
  is_allergic?: string | null;
  vitality_days?: number | null;
  total_revenue: number;
  total_quantity: number;
  times_sold: number;
  unique_customers: number;
}

export interface ProductList {
  product_id: number;
  product_name: string;
  price: number;
  category: string;
  total_revenue: number;
  total_quantity: number;
  revenue_rank: number;
}

export interface PriceDistribution {
  range_label: string;
  min_price: number;
  max_price: number;
  product_count: number;
  total_revenue: number;
  percentage?: number | null;
}

export interface ProductPerformance {
  product_id: number;
  product_name: string;
  price: number;
  total_quantity: number;
  total_revenue: number;
  category: string;
}

// ==========================================
// Customer Types
// ==========================================

export interface CustomerDetail {
  customer_id: number;
  full_name: string;
  city?: string | null;
  country?: string | null;
  total_spent: number;
  total_transactions: number;
  total_quantity: number;
  avg_transaction_value: number;
  unique_products: number;
  first_purchase?: string | null;
  last_purchase?: string | null;
  segment?: string | null;
}

export interface CustomerSegment {
  segment: string;
  customer_count: number;
  total_revenue: number;
  avg_basket: number;
  percentage?: number | null;
}

export interface TopCustomer {
  rank: number;
  customer_id: number;
  full_name: string;
  city: string;
  country: string;
  total_spent: number;
  total_transactions: number;
  segment: string;
}

export interface CustomerActivity {
  month: string;
  year: number;
  active_customers: number;
  new_customers: number;
  total_revenue: number;
}

// ==========================================
// Employee Types
// ==========================================

export interface EmployeeDetail {
  employee_id: number;
  full_name: string;
  gender?: string | null;
  age_group?: string | null;
  seniority_group?: string | null;
  city?: string | null;
  total_revenue: number;
  total_transactions: number;
  total_quantity: number;
  unique_customers: number;
  avg_transaction_value: number;
  revenue_rank: number;
}

export interface EmployeePerformance {
  group_name: string;
  employee_count: number;
  total_revenue: number;
  total_transactions: number;
  avg_revenue_per_employee: number;
}

export interface TopEmployee {
  rank: number;
  employee_id: number;
  full_name: string;
  total_revenue: number;
  total_transactions: number;
  gender?: string | null;
  age_group?: string | null;
}

// ==========================================
// Basket Analysis Types
// ==========================================

export interface BasketRule {
  product1: string;
  product2: string;
  basket_label: string;
  support: number;
  confidence_p1: number;
  confidence_p2: number;
  lift: number;
}

export interface BasketAnalysisResult {
  total_transactions: number;
  total_products: number;
  min_support: number;
  min_lift: number;
  rules: BasketRule[];
  top_rules_by_lift: BasketRule[];
  matrix_data: Array<{ support: number; lift: number; label: string }>;
}

// ==========================================
// Filter Types
// ==========================================

export interface FilterOptions {
  categories: string[];
  countries: string[];
  cities: string[];
  employees: string[];
  date_range: [string | null, string | null];
  products: string[];
  customer_segments: string[];
  age_groups: string[];
  seniority_groups: string[];
}
