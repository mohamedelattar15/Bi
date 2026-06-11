# 🛒 Grocery Sales Dashboard — Frontend

> **Approach 2 (Code)** — Interactive web dashboard built with Next.js, TypeScript, and Recharts.  
> 📁 Location: `Dashboard Version/frontend/`

This frontend application provides a full-featured analytics dashboard for grocery sales data, offering interactive visualizations across five core domains: **Sales Performance**, **Product Portfolio**, **Customer Analytics**, **Employee Performance**, and **Basket Analysis**. It serves as the user-facing layer of the code-oriented approach, consuming the FastAPI backend to render real-time business intelligence.

---

## 📑 Table of Contents

1. [Project Overview](#1-project-overview)
2. [Technology Stack](#2-technology-stack)
3. [Architecture & Folder Structure](#3-architecture--folder-structure)
4. [Pages & Features](#4-pages--features)
   - [4.1 Sales Dashboard (Home)](#41-sales-dashboard-home)
   - [4.2 Product Portfolio](#42-product-portfolio)
   - [4.3 Customer Analytics](#43-customer-analytics)
   - [4.4 Employee Performance](#44-employee-performance)
   - [4.5 Basket Analysis](#45-basket-analysis)
5. [Key Components](#5-key-components)
   - [5.1 Layout Components](#51-layout-components)
   - [5.2 Chart Components](#52-chart-components)
   - [5.3 UI Components](#53-ui-components)
6. [Data Flow & API Integration](#6-data-flow--api-integration)
7. [KPIs, Charts & User Interactions](#7-kpis-charts--user-interactions)
8. [Performance Optimizations](#8-performance-optimizations)
9. [Responsive Design](#9-responsive-design)
10. [Security & Environment Configuration](#10-security--environment-configuration)
11. [Local Development Setup](#11-local-development-setup)
12. [Deployment](#12-deployment)
13. [Screenshots](#13-screenshots)
14. [Future Improvements](#14-future-improvements)

---

## 1. Project Overview

### Objectives

- **Visualize grocery sales data** across multiple dimensions: time, products, customers, employees, and geography.
- **Provide interactive analytics** with date-range filtering, threshold controls, and expandable charts.
- **Enable data-driven decisions** through KPIs, trend analysis, market basket analysis, and customer segmentation.
- **Replicate Power BI dashboards** in a modern web application using open-source technologies.

### Business Context

This dashboard is designed for retail analysts and business managers who need to monitor:

- **Revenue trends** and financial health
- **Product performance** and category breakdowns
- **Customer behavior** and segmentation
- **Employee productivity** and team performance
- **Product associations** for cross-selling opportunities

---

## 2. Technology Stack

| Technology | Version | Role |
|------------|---------|------|
| **Next.js 14** (App Router) | ^14.2.0 | React framework with file-based routing, server/client components |
| **TypeScript** | ^5.6.0 | Type safety across the entire codebase |
| **React 18** | ^18.3.0 | UI component library |
| **Tailwind CSS** | ^3.4.0 | Utility-first CSS framework for rapid styling |
| **Recharts** | ^3.8.1 | Composable charting library built on React components |
| **TanStack React Query** | ^5.56.0 | Server state management, caching, and auto-refetching |
| **Lucide React** | ^1.17.0 | Icon library |
| **shadcn/ui** | — | Accessible, unstyled UI primitives (cards, tables, sliders, badges) |
| **date-fns** | ^4.1.0 | Date manipulation and formatting |
| **clsx / tailwind-merge** | — | Conditional class name merging |

### Why These Technologies?

| Decision | Rationale |
|----------|-----------|
| **Next.js App Router** | File-based routing makes page organization intuitive; supports SSR/SSG for performance |
| **TanStack Query** | Automatic caching (5–10 min stale times), deduplication, and background refetching — critical for a dashboard with 15+ simultaneous API calls |
| **Recharts** | Declarative, composable chart components that integrate naturally with React; supports all chart types needed (bar, line, pie, treemap, scatter, combo) |
| **Tailwind CSS** | Rapid prototyping with utility classes; consistent design system via CSS variables |
| **shadcn/ui** | Unstyled, accessible components that are copy-pasted and fully customizable |

---

## 3. Architecture & Folder Structure

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    NEXT.JS (Frontend)                        │
│                                                              │
│  ┌─────────┐  ┌──────────┐  ┌────────────┐  ┌───────────┐  │
│  │  Pages  │──│  Hooks   │──│  Services  │──│  FastAPI  │  │
│  │ (5 pgs) │  │ (6 hooks)│  │  (api.ts)  │  │  Backend  │  │
│  └─────────┘  └──────────┘  └────────────┘  └───────────┘  │
│       │                                                      │
│  ┌────┴──────────────────────────────────────────────┐      │
│  │              Components Layer                      │      │
│  │  Charts (10) │ Layout (Sidebar, TopNav, Filter)   │      │
│  │  KPIs │ Cards │ Tables │ Sliders │ Badges          │      │
│  └────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### Folder Structure

```
frontend/
├── public/                          # Static assets
├── src/
│   ├── app/                         # Next.js App Router pages
│   │   ├── layout.tsx               # Root layout (sidebar + topnav)
│   │   ├── page.tsx                 # Sales Dashboard (home)
│   │   ├── providers.tsx            # React Query provider
│   │   ├── globals.css              # Global styles + CSS variables
│   │   ├── products/page.tsx        # Product Analysis
│   │   ├── customers/page.tsx       # Customer Analysis
│   │   ├── employees/page.tsx       # Employee Analysis
│   │   └── basket-analysis/page.tsx # Market Basket Analysis
│   │
│   ├── components/
│   │   ├── Sidebar.tsx              # Navigation sidebar
│   │   ├── TopNav.tsx               # Top navigation bar
│   │   ├── KPICard.tsx              # KPI metric display card
│   │   ├── DateRangeFilter.tsx      # Date range selector
│   │   ├── ExpandableChart.tsx      # Expandable chart wrapper
│   │   ├── LoadingSkeleton.tsx       # Loading placeholder
│   │   ├── ChartFilterBar.tsx       # Chart-level filter bar
│   │   ├── FilterDialog.tsx         # Advanced filter dialog
│   │   ├── charts/                  # Recharts chart wrappers
│   │   │   ├── RechartsBarChart.tsx
│   │   │   ├── RechartsDoughnutChart.tsx
│   │   │   ├── RechartsComboChart.tsx
│   │   │   ├── RechartsTreemap.tsx
│   │   │   ├── RechartsScatterChart.tsx
│   │   │   ├── RechartsAreaChart.tsx
│   │   │   ├── RechartsStackedBarChart.tsx
│   │   │   ├── RechartsHeatmapChart.tsx
│   │   │   ├── RechartsWaterfallChart.tsx
│   │   │   └── GaugeCard.tsx
│   │   └── ui/                      # shadcn/ui primitives
│   │       ├── card.tsx, badge.tsx, button.tsx, table.tsx
│   │       ├── slider.tsx, tabs.tsx, select.tsx, input.tsx
│   │       ├── sheet.tsx, separator.tsx, chart.tsx
│   │
│   ├── hooks/                       # React Query hooks
│   │   ├── useDashboard.ts          # Dashboard summary
│   │   ├── useSales.ts              # Sales analytics
│   │   ├── useProducts.ts           # Product analytics
│   │   ├── useCustomers.ts          # Customer analytics
│   │   ├── useEmployees.ts          # Employee analytics
│   │   ├── useBasketAnalysis.ts     # Market basket analysis
│   │   └── useSidebar.tsx           # Sidebar state
│   │
│   ├── services/
│   │   └── api.ts                   # Centralized API client
│   │
│   ├── lib/
│   │   └── utils.ts                 # Formatting utilities
│   │
│   └── types/
│       └── index.ts                 # Shared TypeScript types
│
├── next.config.js
├── tailwind.config.js
├── tsconfig.json
├── package.json
└── .env.local.example
```

---

## 4. Pages & Features

### 4.1 Sales Dashboard (Home)

**Route:** `/` — **File:** `src/app/page.tsx`

The main landing page providing a comprehensive overview of sales performance.

#### KPIs (Row 1)

| KPI | Format | Source | Description |
|-----|--------|--------|-------------|
| **Total Revenue** | Currency | `dashboard.summary.total_revenue` | Total revenue across all sales (€) |
| **Total Profit** | Currency | `insights.growth-metrics.total_profit` | Computed profit (€) |
| **Total Quantity Sold** | Number | `dashboard.summary.total_quantity` | Units sold |
| **Total Transactions** | Number | `dashboard.summary.total_transactions` | Number of sales transactions |
| **Profit Margin** | Percentage | `insights.growth-metrics.profit_margin_pct` | Profit as % of revenue |
| **Average Basket** | Currency | `dashboard.summary.avg_basket` | Average spend per transaction |

#### Charts (Rows 2–6)

| Chart | Type | Data Source | Description |
|-------|------|-------------|-------------|
| **Revenue & Profit Trend** | Combo (Bar + Line) | `sales.over-time` + `sales.ca-growth-by-year` | Monthly revenue with growth % overlay |
| **Month-over-Month Growth** | Bar (colorByValue) | `insights.month-over-month` | MoM growth % with green/red bars |
| **Category Revenue Treemap** | Treemap | `dashboard.summary.sales_by_category` | Revenue distribution by category |
| **Pareto: Top Products** | Table | `insights.pareto-products` | 80/20 product concentration analysis |
| **Top Customers** | Table | `customers.top` | Highest-revenue customers |
| **Sales by City** | Bar (horizontal) | `sales.by-city` | Revenue by geographic area |
| **Top Employees** | Table | `employees.top` | Highest-revenue employees |
| **Customer RFM Segments** | List | `insights.customer-rfm` | Recency/Frequency/Monetary segments |
| **Revenue by Day of Week** | Bar | `insights.revenue-by-day` | Weekday revenue pattern |
| **Revenue by Product Class** | Doughnut | `sales.by-class` | Product class distribution |

#### Interactions
- **Date range filter** at the top filters all charts and KPIs simultaneously
- **Expandable charts** — each chart can be expanded to full-screen for detailed analysis
- **Hover tooltips** on all charts show formatted values and percentages
- **Sortable tables** for top customers, employees, and products

---

### 4.2 Product Portfolio

**Route:** `/products` — **File:** `src/app/products/page.tsx`

Deep-dive into product and category performance.

#### KPIs

| KPI | Description |
|-----|-------------|
| **Total Products** | Number of products in catalog |
| **Categories** | Number of product categories |
| **Average Price** | Mean product price |
| **Total Revenue** | Revenue generated by all products |
| **Top Category %** | Revenue share of the top category |

#### Charts & Tables

| Visualization | Type | Insight |
|---------------|------|---------|
| Category Revenue Treemap | Treemap | Which categories dominate revenue? |
| Price Distribution | Bar | Price range buckets with product counts |
| Price vs Volume Matrix | Scatter | Relationship between price and sales volume |
| Category Growth | Combo | Category revenue trends over time |
| Quantity Summary | Bar | Total quantity sold per category |
| Pareto Product Concentration | Table | 80/20 analysis — which products drive revenue |

---

### 4.3 Customer Analytics

**Route:** `/customers` — **File:** `src/app/customers/page.tsx`

Customer behavior, segmentation, and geographic analysis.

#### KPIs

| KPI | Description |
|-----|-------------|
| **Total Customers** | Unique customer count |
| **Active Customers** | Customers who made a purchase |
| **Loyalty Rate** | Active / Total customers (%) |
| **Avg Basket** | Average spend per transaction |
| **Total Revenue** | Revenue from all customers |
| **Repurchase Rate** | Rate of repeat purchases |

#### Charts & Tables

| Visualization | Type | Insight |
|---------------|------|---------|
| Customer Segmentation | Doughnut | VIP / Loyal / Average / At Risk breakdown |
| Top Customers | Table | Highest-spending customers |
| Active Customers & Revenue | Combo | Customer base growth vs revenue |
| Revenue by City | Treemap | Geographic revenue distribution |
| Avg Basket by City | Bar (horizontal) | Which cities spend more per visit? |
| City Growth Overview | Table | City-level revenue and transaction growth |
| Segment Value Breakdown | List | Avg basket and total revenue by segment |
| Customer Health Dashboard | Cards | Loyalty, repurchase, frequency metrics |

#### RFM Segmentation

The dashboard uses **RFM (Recency, Frequency, Monetary)** analysis to segment customers:

| Segment | Description |
|---------|-------------|
| **Champions** | Biggest spenders, buy most often |
| **Loyal** | High spend, good frequency |
| **Big Spenders** | High monetary value, lower frequency |
| **Frequent Buyers** | Buy often, moderate spend |
| **Average** | Average spend & frequency |
| **At Risk** | Lowest engagement, may churn |

---

### 4.4 Employee Performance

**Route:** `/employees` — **File:** `src/app/employees/page.tsx`

Sales team performance and demographic analysis.

#### KPIs

| KPI | Description |
|-----|-------------|
| **Total Employees** | Active sales staff |
| **Total Revenue** | Revenue generated by all employees |
| **Avg Revenue / Employee** | Mean revenue per staff member |
| **Revenue per Employee** | Total revenue divided by headcount |

#### Charts & Tables

| Visualization | Type | Insight |
|---------------|------|---------|
| Top 5 Employees | Bar | Highest revenue-generating sales reps |
| Performance Table | Table | Employee-level metrics (revenue, transactions, customers) |
| Performance by Age Group | Bar | Revenue distribution across age brackets |
| Performance by Seniority | Bar | Revenue vs years of experience |
| Age Category Distribution | Doughnut | Employee count by age group |
| Gender Distribution | Doughnut | Male / Female employee ratio |
| Revenue by Age Tranche | Bar | CA by age bracket for deeper analysis |

---

### 4.5 Basket Analysis

**Route:** `/basket-analysis` — **File:** `src/app/basket-analysis/page.tsx`

Market basket analysis to discover product associations for cross-selling.

#### KPIs

| KPI | Description |
|-----|-------------|
| **Total Transactions Analyzed** | Total baskets (customer+date groupings) |
| **Products in Scope** | Distinct products considered |
| **Association Rules Found** | Rules meeting current thresholds |
| **Strong Rules (Lift > 2)** | Highly correlated product pairs |

#### Interactive Controls

| Control | Range | Description |
|---------|-------|-------------|
| **Minimum Support slider** | 0.001% – 1% | How often a product pair must appear together |
| **Minimum Lift slider** | 1.0 – 3.0 | How much stronger than random the association must be |

#### Charts & Tables

| Visualization | Type | Insight |
|---------------|------|---------|
| Top 10 Product Pairs | Bar (horizontal) | Highest-lift product associations |
| Association Quality Matrix | Scatter | Support vs Lift — actionable opportunities in top-right quadrant |
| Association Rules Table | Table | Sortable list of all rules with support, confidence, and lift |
| Cross-Sell Opportunity | Card | Strongest association with action recommendation |

#### Metrics

| Metric | Formula | Interpretation |
|--------|---------|---------------|
| **Support** | Pairs(X,Y) / Total Baskets | Frequency of the product pair |
| **Confidence** | Pairs(X,Y) / Baskets(X) | Probability Y is bought when X is bought |
| **Lift** | Support(X,Y) / (Support(X)×Support(Y)) | Association strength vs random |

---

## 5. Key Components

### 5.1 Layout Components

#### `Sidebar.tsx`

Persistent navigation sidebar with 5 links:
- **Sales Performance** (`/`) — Home icon
- **Product Performance** (`/products`) — Package icon
- **Customer Performance** (`/customers`) — Users icon
- **Employee Performance** (`/employees`) — Briefcase icon
- **Basket Analysis** (`/basket-analysis`) — Shopping Cart icon

Active link is highlighted using `usePathname()`. Dark theme with CSS variables.

#### `TopNav.tsx`

Top bar with page title, date range display, and user-facing breadcrumbs.

#### `DateRangeFilter.tsx`

Auto-fetches dataset date boundaries from `/api/filters/` on mount. Provides:
- **Date input fields** (start / end) with min/max constraints
- **Apply button** to trigger data refresh
- **Reset button** to restore full date range
- Calls `onApply(params)` which updates all React Query keys

#### `ExpandableChart.tsx`

Wrapper component that adds a full-screen expand button to any chart. When expanded, renders the chart in a modal-like overlay for detailed analysis.

#### `KPICard.tsx`

Displays a single KPI metric with:
- **Label** (e.g., "Total Revenue")
- **Formatted value** (compact: B/M/K for large numbers, 2 decimal places for currency)
- **Icon** (from Lucide)
- **Trend indicator** (optional up/down/stable arrow with percentage)
- **Hover tooltip** showing the full un-abbreviated value
- Smart formatting: values ≥1B show as `€X.XB`, ≥1M as `€X.XM`, <1K as `€X,XXX.XX`

#### `LoadingSkeleton.tsx`

Skeleton placeholder component shown while data is loading. Displays animated gray rectangles matching the dashboard grid layout.

### 5.2 Chart Components

All chart components are thin wrappers around **Recharts**, providing a consistent API and default styling.

| Component | Recharts Type | Usage |
|-----------|---------------|-------|
| `RechartsBarChart` | `BarChart` | Vertical/horizontal bars with `colorByValue` option (green/red for growth charts) |
| `RechartsDoughnutChart` | `PieChart` | Donut charts with custom tooltip showing name, value, and percentage |
| `RechartsComboChart` | `ComposedChart` | Bars (left axis) + Line (right axis) with compact Y-axis formatting |
| `RechartsTreemapChart` | `Treemap` | Treemap with custom content renderer showing name and value on each cell |
| `RechartsScatterChart` | `ScatterChart` | Scatter plots for support vs lift matrix |
| `RechartsAreaChart` | `AreaChart` | Area charts for cumulative trends |
| `RechartsStackedBarChart` | `BarChart` | Stacked bars for composition analysis |
| `RechartsHeatmapChart` | — | Custom heatmap for category×month revenue |
| `RechartsWaterfallChart` | `BarChart` | Waterfall chart for profit decomposition |
| `GaugeCard` | — | Radial gauge for target vs actual metrics |

#### Shared Chart Features

- **Compact Y-axis ticks**: Large values formatted as B/M/K (e.g., `1.1B`, `650M`)
- **Percentage axis**: Growth charts show `%` suffix
- **Smart tooltips**: Currency values formatted with `€` prefix; growth rates show `+/-%` with green/red coloring
- **Color-by-value**: Growth charts color bars/dots green (≥0) or red (<0)
- **Responsive**: All charts use `w-full` with percentage-based sizing

### 5.3 UI Components (shadcn/ui)

| Component | File | Usage |
|-----------|------|-------|
| `Card` | `card.tsx` | Dashboard card containers with header/content |
| `Table` | `table.tsx` | Data tables for top customers, employees, products |
| `Slider` | `slider.tsx` | Support and Lift threshold controls |
| `Badge` | `badge.tsx` | Segment labels and status indicators |
| `Tabs` | `tabs.tsx` | Tabbed chart views (if applicable) |
| `Select` | `select.tsx` | Dropdown filters (if applicable) |
| `Sheet` | `sheet.tsx` | Slide-out panel for filters |
| `Button` | `button.tsx` | Action buttons |
| `Input` | `input.tsx` | Date inputs |
| `Separator` | `separator.tsx` | Visual dividers |

---

## 6. Data Flow & API Integration

### Data Flow Diagram

```
User Action (filter change, page load)
        │
        ▼
React Component (page.tsx)
        │
        ▼
React Query Hook (useDashboard, useSales...)
        │
        ▼
API Service (api.ts → fetchApi)
        │
        ▼
FastAPI Backend (localhost:8000)
        │
        ▼
PostgreSQL Database
        │
        ▼
JSON Response → React Query Cache (staleTime: 5-10 min)
        │
        ▼
Component re-renders with cached/formatted data
```

### API Client (`src/services/api.ts`)

Centralized module with:
- **`fetchApi<T>()`** — Generic fetch wrapper with error handling, JSON parsing, and typed responses
- **`ApiError`** — Custom error class with HTTP status code
- **`buildSearchParams()`** — Helper to construct query strings from filter parameters
- **API modules**: `dashboardApi`, `salesApi`, `productsApi`, `customersApi`, `employeesApi`, `basketApi`, `filtersApi`, `insightsApi`

### Data Fetching Strategy

| Pattern | Implementation |
|---------|---------------|
| **Caching** | TanStack Query with `staleTime` of 5–10 minutes |
| **Auto-refetch** | Disabled (`refetchOnWindowFocus: false`) for stability |
| **Deduplication** | Same query keys share a single request |
| **Parallel fetching** | All hooks fire simultaneously on page load |
| **Error handling** | Each page has an error state with user-friendly message |
| **Loading states** | `LoadingSkeleton` shown until all critical data arrives |

### Query Key Convention

```
["domain", "endpoint", ...params]
```

Examples:
- `["dashboard", "summary", { start_date, end_date }]`
- `["sales", "over-time", { start_date, end_date, category }]`
- `["customers", "top", 10]`

---

## 7. KPIs, Charts & User Interactions

### Value Formatting (`src/lib/utils.ts`)

All formatting is centralized for consistency:

```typescript
formatCurrency(value)        // €4.4B, €650M, €650.71
formatCompactNumber(value)   // 85.7M, 6.7M, 452
formatPercentage(value)      // 100.0%, 4.92%
formatDate(dateStr)          // "Jan 2018", "Dec 2022"
```

**Compact notation logic:**
- ≥ 1 000 000 000 → `X.XB`
- ≥ 1 000 000 → `X.XM`
- ≥ 1 000 → `X.XK`
- < 1 000 → Full number with commas

### User Interactions

| Interaction | Component | Behavior |
|-------------|-----------|----------|
| **Date range filter** | `DateRangeFilter` | Auto-fetches min/max dates; updates all query keys |
| **Chart expansion** | `ExpandableChart` | Toggles full-screen overlay with the same chart |
| **Threshold sliders** | `Slider` (basket page) | Real-time updates to `minSupport`/`minLift` state |
| **Hover tooltip** | `ChartTooltip` | Formatted value display on all charts |
| **Color-by-value** | `RechartsBarChart` | Bars colored green (growth) / red (decline) |
| **Segment descriptions** | RFM card (collapsible) | Click to reveal segment meanings |
| **Table sorting** | Native HTML tables | Sortable by clicking column headers |

---

## 8. Performance Optimizations

### Caching Strategy

| Technique | Implementation | Impact |
|-----------|---------------|--------|
| **React Query staleTime** | 5–10 min per endpoint | Prevents redundant API calls on page navigation |
| **Parallel data fetching** | All hooks run simultaneously | ~1.5s total load time instead of 15s sequential |
| **Materialized views (backend)** | Pre-aggregated tables | Backend query time reduced from 5s to ~50ms |

### Rendering Optimizations

| Technique | Implementation |
|-----------|---------------|
| **`"use client"`** | Pages marked as client components for interactive features |
| **Conditional rendering** | Chart data computed only when API response is available |
| **Loading skeleton** | Animated placeholders prevent layout shift (CLS) |
| **Overflow scrolling** | Tables with `max-h-[320px] overflow-y-auto` for large datasets |

### Bundle Size

- **Tree-shaking** via ES modules (only imported chart types are bundled)
- **No runtime CSS-in-JS** — Tailwind generates static CSS at build time
- **Icons imported individually** from `lucide-react` (no full icon set bundle)

---

## 9. Responsive Design

### Breakpoints

| Breakpoint | Width | Layout |
|------------|-------|--------|
| **Default** | < 640px | Single column, stacked KPIs |
| **`sm`** | ≥ 640px | 2-column KPI grid |
| **`lg`** | ≥ 1024px | 2-column chart layout |
| **`xl`** | ≥ 1280px | 6-column KPI grid, 2-column charts |

### Dashboard Grid

```tsx
// KPI cards: 1 → 2 → 3 → 6 columns
<div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">

// Charts: always 2 columns on large screens
<div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
```

### Mobile Considerations

- Sidebar remains visible on all screen sizes (fixed 260px width)
- Tables use horizontal scroll (`overflow-x-auto`) on narrow screens
- Charts auto-resize via Recharts `ResponsiveContainer`
- Font sizes use `text-sm`/`text-xs` for compact display

---

## 10. Security & Environment Configuration

### Environment Variables

```env
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | No | `http://localhost:8000` | FastAPI backend URL |

### Security Considerations

| Concern | Mitigation |
|---------|------------|
| **API exposure** | Backend is expected to run on localhost/internal network |
| **CORS** | Handled by FastAPI middleware (allows all origins in dev) |
| **Sensitive data** | No authentication implemented (internal tool) |
| **XSS** | React's automatic escaping prevents injection |
| **Environment variables** | `.env.local` excluded from version control via `.gitignore` |

---

## 11. Local Development Setup

### Prerequisites

- **Node.js**: 18+ (recommended: 20 LTS)
- **Bun**: Package manager and runtime (or npm/pnpm)
- **Backend**: FastAPI server running on `http://localhost:8000`

### Installation

```bash
cd "Dashboard Version/frontend"

# Install dependencies
bun install
# OR: npm install
# OR: pnpm install

# Create environment file
cp .env.local.example .env.local
```

### Environment Configuration

```env
# .env.local — customize if backend runs on a different port
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Running in Development

```bash
# Start the development server
bun run dev
# OR: npm run dev

# Open http://localhost:3000
```

The development server supports:
- **Hot Module Replacement (HMR)** — instant updates on file changes
- **TypeScript errors** displayed in-browser
- **ESLint warnings** in terminal

### Building for Production

```bash
# Create optimized production build
bun run build
# OR: npm run build

# Start production server
bun run start
# OR: npm run start
```

### Common Issues

| Issue | Solution |
|-------|----------|
| **Backend not reachable** | Ensure FastAPI is running: `http://localhost:8000/api/health` |
| **Port 3000 in use** | Next.js will automatically try 3001, 3002... |
| **TypeScript errors** | Run `npx tsc --noEmit` to check types |
| **Missing dependencies** | Run `bun install` again |

---

## 12. Deployment

### Build Options

Next.js is configured with `output: 'standalone'` in `next.config.js`, producing a self-contained deployment package.

```bash
# Build standalone output
bun run build
# Output in: .next/standalone/
```

### Docker Deployment

For a complete Docker setup with all 3 services (frontend, backend, database), see:

```bash
cd "Dashboard Version/docker"
docker compose up -d
```

This starts:
- **Frontend**: `http://localhost:3000`
- **Backend API**: `http://localhost:8000`
- **PostgreSQL**: `localhost:5432`

### Manual Deployment

```bash
# 1. Build
cd frontend
bun run build

# 2. Copy standalone output to server
cp -r .next/standalone/* /opt/app/
cp -r .next/static /opt/app/.next/

# 3. Set environment variables
export NEXT_PUBLIC_API_URL=https://api.yourdomain.com

# 4. Start
node server.js
```

### Environment-Specific Configuration

| Environment | `NEXT_PUBLIC_API_URL` | Notes |
|-------------|----------------------|-------|
| **Local dev** | `http://localhost:8000` | Default |
| **Docker Compose** | `http://backend:8000` | Internal Docker network |
| **Production** | `https://api.yourdomain.com` | TLS-enabled endpoint |

---

## 13. Screenshots

> *Screenshots to be added. Each page should be captured with representative data loaded.*

### Page Previews

| Page | Description |
|------|-------------|
| **Sales Dashboard** | KPI cards + 5 chart panels + data tables |
| **Products Page** | Category treemap, price distribution, Pareto table |
| **Customers Page** | RFM segments, geographic treemap, loyalty dashboard |
| **Employees Page** | Top performers, demographics, seniority analysis |
| **Basket Analysis** | Threshold sliders, association rules, scatter matrix |

---

## 14. Future Improvements

| Area | Improvement | Priority |
|------|-------------|----------|
| **Authentication** | Add login system (NextAuth, JWT) for production deployment | High |
| **Export** | Add CSV/Excel download for KPI data and tables | Medium |
| **Real-time** | WebSocket connection for live data updates | Low |
| **Dark/Light mode** | Toggle between themes | Low |
| **Print reports** | Print-optimized CSS for PDF generation | Medium |
| **Internationalization** | Multi-language support (i18n) | Low |
| **Accessibility** | ARIA labels, keyboard navigation, screen reader support | Medium |
| **Testing** | Add Jest + Cypress test suite | High |
| **Storybook** | Component library documentation | Low |
| **PWA** | Progressive web app for offline access | Low |

---

> **Project**: Grocery Sales BI Dashboard — Approach 2 (Code)  
> **Frontend**: Next.js 14 + TypeScript + Recharts + Tailwind CSS  
> **Documentation updated**: June 2026
