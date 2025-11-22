function App() {

  return (
    <div className="bg-gray-500 min-h-screen flex flex-col items-center justify-center">
      <h1 className="text-3xl">
        Login
      </h1>
      <button 
        className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        onClick={() => window.location.href = "http://127.0.0.1:8000/oauth"}
        >
          Login with MAL
      </button>
    </div>
  );
}

export default App;
