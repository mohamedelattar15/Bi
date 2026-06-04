"use client";

import { usePathname } from "next/navigation";
import { Bell, RefreshCw } from "lucide-react";

const pageTitles: Record<string, string> = {
  "/": "Sales Dashboard",
  "/products": "Product Analysis",
  "/customers": "Customer Analysis",
  "/employees": "Employee Analysis",
  "/basket-analysis": "Basket Analysis",
};

export function TopNav() {
  const pathname = usePathname();
  const title = pageTitles[pathname] || "Dashboard";

  return (
    <header className="flex h-16 items-center justify-between border-b border-gray-200 bg-white px-6">
      <div>
        <h1 className="text-xl font-semibold text-gray-900">{title}</h1>
        <p className="text-sm text-gray-500">
          Grocery Sales Analytics Dashboard
        </p>
      </div>

      <div className="flex items-center gap-3">
        <button
          onClick={() => window.location.reload()}
          className="rounded-lg p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-600"
          title="Refresh"
        >
          <RefreshCw className="h-5 w-5" />
        </button>
        <button
          className="rounded-lg p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-600"
          title="Notifications"
        >
          <Bell className="h-5 w-5" />
        </button>
      </div>
    </header>
  );
}
