import React from 'react'
import { createRoot } from 'react-dom/client'
import App from './App'
import './index.css'

createRoot(document.getElementById('root')).render(<App />)

// Register service worker (optional in dev)
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js')
}
