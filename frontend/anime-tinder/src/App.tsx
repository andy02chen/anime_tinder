import { useState } from "react";

function App() {
  const [msg, setMsg] = useState("");

  const fetchMessage = async () => {
    const res = await fetch("http://127.0.0.1:8000/hello");
    const data = await res.json();
    setMsg(data.message);
  };

  return (
    <div className="bg-gray-500 min-h-screen flex flex-col items-center justify-center">
      <h1 className="text-3xl">
        Frontend ↔ Backend Test
      </h1>
      <button 
        className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        onClick={fetchMessage}>
          Ping Backend
      </button>
      <p>
        {msg}
      </p>
    </div>
  );
}

export default App;
