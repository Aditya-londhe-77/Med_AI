import { Link, useLocation } from "react-router-dom";
import { 
  Activity, 
  Stethoscope, 
  Network, 
  History, 
  Settings, 
  Bot
} from "lucide-react";
import { cn } from "@/lib/utils";

export function MedicalSidebar() {
  const location = useLocation();

  const links = [
    { name: "Medical Dashboard", href: "/", icon: Activity },
    { name: "Medical Workspace", href: "/workspace", icon: Stethoscope },
    { name: "Agent Center", href: "/agents", icon: Bot },
    { name: "Knowledge Explorer", href: "/graph", icon: Network },
    { name: "Research History", href: "/history", icon: History },
    { name: "System Settings", href: "/settings", icon: Settings },
  ];

  return (
    <aside className="hidden w-64 shrink-0 flex-col border-r border-[#E9E2F2] bg-white/80 backdrop-blur-xl md:flex">
      {/* Brand Header */}
      <div className="flex h-20 items-center border-b border-[#E9E2F2] px-6">
        <div className="mr-3 flex h-10 w-10 items-center justify-center rounded-2xl bg-gradient-to-tr from-[#7652D6] to-[#E879B9] text-white shadow-md shadow-[#7652D6]/20">
          <Stethoscope className="h-5 w-5" />
        </div>
        <div>
          <h1 className="text-base font-bold tracking-tight text-[#29243A]">AISIA</h1>
          <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-[#7652D6]">
            Medical AI Swarm
          </p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1.5 p-4">
        {links.map((link) => {
          const Icon = link.icon;
          const isActive = location.pathname === link.href;

          return (
            <Link
              key={link.name}
              to={link.href}
              className={cn(
                "group flex items-center rounded-2xl px-3.5 py-3 text-xs md:text-sm font-semibold transition-all duration-200 select-none",
                isActive
                  ? "bg-gradient-to-r from-[#F3EEFF] to-[#FFF1F7] text-[#4B2B91] shadow-sm font-bold border border-[#E9E2F2]"
                  : "text-[#777187] hover:bg-[#F3EEFF]/50 hover:text-[#29243A]"
              )}
            >
              <Icon
                className={cn(
                  "mr-3 h-[18px] w-[18px] transition-transform group-hover:scale-110",
                  isActive ? "text-[#7652D6]" : "text-[#777187]"
                )}
              />
              {link.name}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
