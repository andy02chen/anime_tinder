"use client"

import React, { useState } from 'react'

const Login = () => {
  const [msg, setMsg] = useState<string>("");

  const fetchHello = async () => {
    try {
      const res = await fetch("http://localhost:8000/hello");
      const data = await res.json();
      setMsg(data.message);
    } catch (error) {
      setMsg("Failed to fetch message");
    }
  };

  return (
    <div className='rounded-xl border-1 border-blue-400 p-8'> 
      <h1 className='font-bold text-2xl'>
        <button
          onClick={fetchHello}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Fetch Hello World
        </button>
        {msg && <p className="mt-2 text-lg">{msg}</p>}
      </h1>
    </div>
  )
}

export default Login