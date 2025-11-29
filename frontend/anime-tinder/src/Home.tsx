import { useEffect } from "react";

interface HomeProps {
  setUser: (user: { id: number; username: string } | null) => void;
}

export default function Home({ setUser }: HomeProps) {
  return (
    <div className=" text-white">
      Yokoso
    </div>
  );
}
