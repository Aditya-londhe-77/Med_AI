import { Outlet } from "react-router-dom";
import { MedicalTopbar } from "./MedicalTopbar";

export function MedicalAppShell() {
  return (
    <div className="min-h-screen w-full flex flex-col bg-[#FFF0F5] text-foreground antialiased selection:bg-pink-300/30">
      {/* Top Navigation Bar with Dashboard, Workshop, Topics, etc. */}
      <MedicalTopbar />

      {/* Main Content Area */}
      <main className="flex-1 w-full overflow-y-auto px-4 py-8 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-7xl">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
