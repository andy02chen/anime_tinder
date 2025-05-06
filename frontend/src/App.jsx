import { useEffect, useState } from 'react'

function App() {
  const [message, setMessage] = useState("Loading...")

  useEffect(() => {
    fetch("http://localhost:8000/api/hello")
      .then((res) => res.json())
      .then((data) => setMessage(data.message))
      .catch((err) => setMessage("Failed to connect to backend"))
  }, [])

  return (
    <div style={{ padding: 40, fontSize: 24 }}>
      {message}
    </div>
  )
}

export default App
