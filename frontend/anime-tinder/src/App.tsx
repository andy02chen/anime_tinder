import { useState, useEffect, type JSX } from "react";
import { BrowserRouter, Routes, Route, useNavigate, Navigate } from "react-router-dom";
import Home from "./Home";
import { ToastContainer, toast } from 'react-toastify';
import Login from "./Login";

// Wrapper to handle protected routes
function ProtectedRoute({ user, children }: { user: any; children: JSX.Element }) {
  if (!user) {
    return <Navigate to="/" replace />;
  }
  return children;
}

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
          toast.error(err.error || "Session expired. Please log in again.");
          return;
        }

        const data = await res.json();
        if (data.user) {
          setUser(data.user);
          navigate("/home", { replace: true });
        }
      } catch (err) {
        console.log(err);
        toast.error("Failed to check session. Please try again.");
      } finally {
        setLoading(false);
      }
    }

    checkSession();
  }, [navigate]);

  // Show nothing / loader while session is being checked
  // TODO loading indicator
  if (loading) return <div className="text-black">Loading...</div>;

  return (
    <main className="bg-gray-500 min-h-screen">
      <Login/>
      {!user && (
        <div className="h-screen flex flex-col items-center justify-center">
          <h1 className="text-3xl text-white">Login</h1>
          <button
            className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            onClick={() => {
              window.location.href = "http://127.0.0.1:8000/oauth";
            }}
          >
            Login with MAL
          </button>
        </div>
      )}

      <Routes>
        <Route path="/login"/>
        <Route
          path="/home"
          element={
            <ProtectedRoute user={user}>
              <Home setUser={setUser} />
            </ProtectedRoute>
          }
        />
        {/* Catch-all route → redirect to landing page */}
        <Route path="*" element={<Navigate to="/" replace />} />
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
