import { useState, useEffect } from "react";
import { BrowserRouter, Routes, Route, useNavigate } from "react-router-dom";

function AppWrapper() {
  return (
    <BrowserRouter>
      <App />
    </BrowserRouter>
  );
}

function App() {
  const [user, setUser] = useState<{ id: number; username: string } | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    async function checkSession() {
      try {
        const res = await fetch("http://127.0.0.1:8000/api/session", {
          method: "GET",
          credentials: "include",
        });
        if (res.ok) {
          const data = await res.json();
          if (data.user) {
            setUser(data.user);
            navigate("/home", { replace: true });
          }
        }
      } catch (err) {
        console.error("Session check failed", err);
      }
    }

    checkSession();
  }, [navigate]);

  return (
    <>
      <div className="bg-gray-500 min-h-screen flex flex-col items-center justify-center">
        <h1 className="text-3xl text-white">Login</h1>

        {!user && (
          <button
            className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            onClick={() => {
              window.location.href = "http://127.0.0.1:8000/oauth";
            }}
          >
            Login with MAL
          </button>
        )}

        {user && (
          <div className="mt-4 text-white">
            Logged in as: <strong>{user.username}</strong>
          </div>
        )}
      </div>
    </>
  );
}

export default AppWrapper;
