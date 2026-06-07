"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  BarChart3,
  Package,
  Users,
  Briefcase,
  ShoppingCart,
  Home,
} from "lucide-react";

const navItems = [
  { href: "/", label: "Sales Dashboard", icon: Home },
  { href: "/products", label: "Products", icon: Package },
  { href: "/customers", label: "Customers", icon: Users },
  { href: "/employees", label: "Employees", icon: Briefcase },
  { href: "/basket-analysis", label: "Basket Analysis", icon: ShoppingCart },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex w-64 flex-col border-r border-gray-200 bg-white">
      {/* Logo */}
      <div className="flex h-16 items-center gap-2 border-b border-gray-200 px-6">
        <BarChart3 className="h-7 w-7 text-blue-600" />
        <span className="text-lg font-bold text-gray-900">
          Grocery BI
        </span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 px-3 py-4">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                isActive
                  ? "bg-blue-50 text-blue-700"
                  : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
              )}
            >
              <Icon className="h-5 w-5" />
              {item.label}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="border-t border-gray-200 px-6 py-4">
        <p className="text-xs text-gray-400">
          Powered by Next.js & FastAPI
        </p>
      </div>
    </aside>
  );
}
