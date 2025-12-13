import { useState, useEffect} from "react";
import { BrowserRouter, Routes, Route, useNavigate, Navigate } from "react-router-dom";
import Home from "./Home";
import Loader from "./Loader";
import Onboarding from "./Onboarding";
import ProtectedRoute from "./ProtectedRoute";

// Main App component
function AppContent() {
  const [user, setUser] = useState<{ id: number; username: string } | null>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    async function checkSession() {
      try {
        const res = await fetch("http://127.0.0.1:8000/api/session", {
          method: "GET",
          credentials: "include",
        });

        if (!res.ok) {
          const err = await res.json();
          console.log(err);
          return;
        }

        const data = await res.json();
        if (data.user) {
          setUser(data.user);
          const userRes = await fetch("http://127.0.0.1:8000/api/user", {
            credentials: "include",
          });
          const userData = await userRes.json();

          if (userData.is_new_user) {
            navigate("/onboarding", { replace: true });
          } else {
            navigate("/home", { replace: true });
          }
        }
      } catch (err) {
        console.log(err);
      } finally {
        setLoading(false);
      }
    }

    checkSession();
  }, [navigate]);

  return (
    <main className="bg-gray-500 min-h-screen flex items-center justify-center">
      {loading && <Loader />}

      {!loading && !user && (
        <div className="h-screen flex flex-col items-center justify-center">
          <h1 className="text-3xl text-white">Login</h1>
          <button
            className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            onClick={() => (window.location.href = "http://127.0.0.1:8000/oauth")}
          >
            Login with MAL
          </button>
        </div>
      )}

      <Routes>
        <Route
          path="/onboarding"
          element={
            <ProtectedRoute user={user} loading={loading}>
              <Onboarding />
            </ProtectedRoute>
          }
        />
        <Route
          path="/home"
          element={
            <ProtectedRoute user={user} loading={loading}>
              <Home />
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<Navigate to="/home" replace />} />
      </Routes>
    </main>
  );
}

// Wrap AppContent with BrowserRouter
export default function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
}
