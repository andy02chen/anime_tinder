"use client"

import React, { useState } from 'react'

const Login = () => {
  const [msg, setMsg] = useState<string>("");

  const oauth = async () => {
    try {
      const res = await fetch("http://localhost:8000/oauth");
      const data = await res.json();
      setMsg(data.message);
    } catch (error) {
      setMsg("Failed to start OAuth");
    }
  }

  return (
    <div className='rounded-xl border-1 border-blue-400 p-8'> 
      <h1 className='font-bold text-2xl'>
        <button
          onClick={oauth}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Login with MAL
        </button>
        {msg && <p className="mt-2 text-lg">{msg}</p>}
      </h1>
    </div>
  )
}

export default Login