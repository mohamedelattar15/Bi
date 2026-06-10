"use client";

import { usePathname } from "next/navigation";
import { Bell, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";

const pageTitles: Record<string, string> = {
  "/": "Sales Performence",
  "/products": "Product Performence",
  "/customers": "Costumer Performence",
  "/employees": "Employee Performence",
  "/basket-analysis": "Basket Analysis",
};

export function TopNav() {
  const pathname = usePathname();
  const title = pageTitles[pathname] || "Dashboard";

  return (
    <header className="flex h-16 items-center justify-between border-b border-border bg-card px-6">
      <div>
        <h1 className="text-xl font-semibold text-foreground">{title}</h1>
        <p className="text-sm text-muted-foreground">
          Grocery Sales Analytics Dashboard
        </p>
      </div>

      <div className="flex items-center gap-2">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => window.location.reload()}
          title="Refresh"
        >
          <RefreshCw className="h-5 w-5" />
        </Button>
        <Button
          variant="ghost"
          size="icon"
          title="Notifications"
        >
          <Bell className="h-5 w-5" />
        </Button>
      </div>
    </header>
  );
}
