import { Link, useLocation } from "react-router-dom";
import { 
  Stethoscope, 
  Activity, 
  Network, 
  History, 
  Settings, 
  Bot, 
  HeartHandshake
} from "lucide-react";
import { ThemeToggle } from "@/components/ThemeToggle";
import { cn } from "@/lib/utils";

export function MedicalTopbar() {
  const location = useLocation();

  const navLinks = [
    { name: "Medical Dashboard", href: "/", icon: Activity },
    { name: "Medical Workshop", href: "/workspace", icon: Stethoscope },
    { name: "Health Topics", href: "/graph", icon: Network },
    { name: "AI Health Helpers", href: "/agents", icon: Bot },
    { name: "Search History", href: "/history", icon: History },
    { name: "Settings", href: "/settings", icon: Settings },
  ];

  return (
    <header className="sticky top-0 z-30 w-full border-b border-pink-200/80 bg-white/95 backdrop-blur-md shadow-xs">
      <div className="mx-auto flex h-18 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        
        {/* Brand Logo & Name */}
        <Link to="/" className="flex items-center gap-3 shrink-0 group">
          <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-gradient-to-tr from-[#7652D6] via-[#E879B9] to-[#F472B6] text-white shadow-md shadow-pink-500/20 group-hover:scale-105 transition-transform">
            <HeartHandshake className="h-6 w-6" />
          </div>
          <div className="flex flex-col">
            <span className="text-sm sm:text-base font-extrabold tracking-tight text-[#29243A] leading-tight">
              AI Based Strategic Intelligence Assistant Medical AI
            </span>
            <span className="text-[11px] font-semibold text-pink-600">
              Clear & Simple Health Answers
            </span>
          </div>
        </Link>

        {/* Desktop Navigation Links */}
        <nav className="hidden lg:flex items-center gap-1.5" aria-label="Main Navigation">
          {navLinks.map((link) => {
            const Icon = link.icon;
            const isActive = location.pathname === link.href;

            return (
              <Link
                key={link.name}
                to={link.href}
                className={cn(
                  "flex items-center gap-2 rounded-full px-3.5 py-1.5 text-xs font-bold transition-all duration-150 select-none",
                  isActive
                    ? "bg-[#FFF0F5] text-[#7652D6] border border-pink-200/90 shadow-xs"
                    : "text-[#777187] hover:bg-pink-50 hover:text-[#29243A]"
                )}
              >
                <Icon
                  className={cn(
                    "h-3.5 w-3.5 transition-transform",
                    isActive ? "text-[#7652D6]" : "text-[#777187]"
                  )}
                />
                <span>{link.name}</span>
              </Link>
            );
          })}
        </nav>

        {/* Right Status & Theme Controls */}
        <div className="flex items-center gap-2 sm:gap-3 shrink-0">
          <ThemeToggle />
        </div>
      </div>

      {/* Secondary Sub-Navbar for Tablets and Mobile */}
      <div className="flex lg:hidden overflow-x-auto border-t border-pink-100 bg-[#FFF5F9] px-4 py-2 scrollbar-none gap-2">
        {navLinks.map((link) => {
          const Icon = link.icon;
          const isActive = location.pathname === link.href;

          return (
            <Link
              key={link.name}
              to={link.href}
              className={cn(
                "flex items-center gap-1.5 whitespace-nowrap rounded-full px-3 py-1.5 text-xs font-semibold shrink-0 transition-colors",
                isActive
                  ? "bg-white text-[#7652D6] font-bold border border-pink-200 shadow-xs"
                  : "text-[#777187] hover:text-[#29243A]"
              )}
            >
              <Icon className="h-3.5 w-3.5" />
              <span>{link.name}</span>
            </Link>
          );
        })}
      </div>
    </header>
  );
}
