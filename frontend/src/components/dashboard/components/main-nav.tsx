import React from "react";
import { Link, useLocation } from "react-router-dom";
import { cn } from "@/lib/utils";
import { FileText } from "lucide-react";

export function MainNav({
  className,
  ...props
}: React.HTMLAttributes<HTMLElement>) {
  const location = useLocation();

  const routes = [
    {
      href: "/dashboard",
      label: "Dashboard",
      active: location.pathname === "/dashboard",
    },
    {
      href: "/knowledge",
      label: "Knowledge Base",
      icon: FileText,
      active: location.pathname.startsWith("/knowledge"),
    },
  ];

  return (
    <nav
      className={cn("flex items-center space-x-4 lg:space-x-6", className)}
      {...props}
    >
      {routes.map((route) => (
        <Link
          key={route.href}
          to={route.href}
          className={cn(
            "flex items-center text-sm font-medium transition-colors hover:text-primary",
            route.active
              ? "text-black dark:text-white"
              : "text-muted-foreground"
          )}
        >
          {route.icon && <route.icon className="w-4 h-4 mr-2" />}
          {route.label}
        </Link>
      ))}
    </nav>
  );
}
