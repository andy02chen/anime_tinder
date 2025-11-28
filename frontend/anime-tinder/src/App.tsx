import { useState } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./Home";

function App() {
  const [accessToken, setAccessToken] = useState<string | null>(null);

  return (
    <BrowserRouter>
      <div className="bg-gray-500 min-h-screen flex flex-col items-center justify-center">

        <h1 className="text-3xl text-white">Login</h1>

        {!accessToken && (
          <button
            className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            onClick={() => {
              window.location.href = "http://127.0.0.1:8000/oauth";
            }}
          >
            Login with MAL
          </button>
        )}

        {accessToken && (
          <div className="mt-4 text-white">
            Logged in! Access Token: {accessToken}
          </div>
        )}
      </div>

      <Routes>
        <Route
          path="/home"
          element={<Home setAccessToken={setAccessToken} />}
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
