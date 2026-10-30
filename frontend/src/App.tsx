import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { supabase } from "./services/supabase";
import { Layout } from "./components/layout/Layout";
import { Dashboard } from "./pages/Dashboard";
import { MedicalWorkspace } from "./pages/MedicalWorkspace";
import { QueryExecution } from "./pages/QueryExecution";
import { Results } from "./pages/Results";
import { History } from "./pages/History";
import { KnowledgeGraph } from "./pages/KnowledgeGraph";
import { AgentConfig } from "./pages/AgentConfig";
import { Login } from "./pages/Login";
import { Signup } from "./pages/Signup";

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const [session, setSession] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // 1. Check for active local clinical session (for offline / demo / viva presentation)
    const localSession = localStorage.getItem("aisia_session") || localStorage.getItem("aegis_session");
    if (localSession) {
      try {
        setSession(JSON.parse(localSession));
        setLoading(false);
        return;
      } catch (e) {
        localStorage.removeItem("aisia_session");
        localStorage.removeItem("aegis_session");
      }
    }

    // 2. Otherwise check Supabase auth
    try {
      supabase.auth.getSession().then(({ data }) => {
        if (data?.session) {
          setSession(data.session);
        }
        setLoading(false);
      }).catch(() => {
        setLoading(false);
      });

      const {
        data: { subscription },
      } = supabase.auth.onAuthStateChange((_event, session) => {
        if (session) {
          setSession(session);
        }
      });

      return () => subscription.unsubscribe();
    } catch {
      setLoading(false);
    }
  }, []);

  if (loading) {
    return (
      <div className="h-screen w-full flex items-center justify-center bg-background text-[#4B2B91] font-sans text-sm font-semibold">
        Authenticating AISIA Medical Portal...
      </div>
    );
  }

  if (!session) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
          {/* 1. Medical AI Dashboard */}
          <Route index element={<Dashboard />} />
          {/* 2. Medical AI Workspace */}
          <Route path="workspace" element={<MedicalWorkspace />} />
          {/* 3. Live Agent Orchestration */}
          <Route path="query/:id" element={<QueryExecution />} />
          {/* 4. Medical Report Viewer */}
          <Route path="results/:id" element={<Results />} />
          {/* 5. Medical Agent Center */}
          <Route path="agents" element={<AgentConfig />} />
          {/* 6. Medical Knowledge Explorer */}
          <Route path="graph" element={<KnowledgeGraph />} />
          {/* 7. Research History */}
          <Route path="history" element={<History />} />
          {/* 8. System Settings */}
          <Route path="settings" element={<AgentConfig />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
