import { useEffect } from "react";

interface HomeProps {
  setUser: (user: { id: number; username: string } | null) => void;
}

export default function Home({ setUser }: HomeProps) {
  useEffect(() => {
    async function loadSession() {
      const res = await fetch("http://127.0.0.1:8000/api/session", {
        method: "GET",
        credentials: "include",
      });

      const data = await res.json();

      if (data.user) {
        setUser(data.user);
      } else {
        console.error("Session load failed:", data);
        setUser(null);
      }
    }

    loadSession();
  }, [setUser]);

  return <div className="text-white">Loading your session...</div>;
}
