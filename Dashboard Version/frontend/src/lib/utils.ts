import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/** Format a number as currency with smart compact notation.
 *
 * Handles both `number` and `string` values (backend sends Decimal as string).
 *
 * - Values >= 1B → "€X.XB"
 * - Values >= 1M → "€X.XM"
 * - Values >= 1K → "€X.XK"
 * - Otherwise    → "€X,XXX.XX"
 */
export function formatCurrency(value: number | string, currency = "€"): string {
  const num = typeof value === "string" ? parseFloat(value) : value;
  if (num >= 1_000_000_000) {
    return `${currency}${(num / 1_000_000_000).toFixed(1)}B`;
  }
  if (num >= 1_000_000) {
    return `${currency}${(num / 1_000_000).toFixed(1)}M`;
  }
  if (num >= 1_000) {
    return `${currency}${(num / 1_000).toFixed(1)}K`;
  }
  return `${currency}${num.toLocaleString("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

/** Format a large number with compact notation.
 *
 * Handles both `number` and `string` values.
 */
export function formatCompactNumber(value: number | string): string {
  const num = typeof value === "string" ? parseFloat(value) : value;
  if (num >= 1_000_000_000) return `${(num / 1_000_000_000).toFixed(1)}B`;
  if (num >= 1_000_000) return `${(num / 1_000_000).toFixed(1)}M`;
  if (num >= 1_000) return `${(num / 1_000).toFixed(1)}K`;
  return num.toString();
}

/** Format percentage */
export function formatPercentage(value: number): string {
  return `${value.toFixed(1)}%`;
}

/** Format date to readable string */
export function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString("en-US", {
    year: "numeric", month: "short", day: "numeric",
  });
}
