import { useEffect } from "react";

interface LoggedInProps {
  setAccessToken: (token: string | null) => void;
}

export default function Home({ setAccessToken }: LoggedInProps) {
  useEffect(() => {
    async function loadSession() {
      const res = await fetch("http://127.0.0.1:8000/api/session", {
        method: "GET",
        credentials: "include", // sends HttpOnly cookie
      });

      const data = await res.json();

      if (data.access_token) {
        setAccessToken(data.access_token);
      } else {
        console.error("Session load failed:", data);
        setAccessToken(null);
      }
    }

    loadSession();
  }, [setAccessToken]);

  return <div className="text-white">Logging you in...</div>;
}
