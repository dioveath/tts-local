import React from 'react'
import './App.css'
import { Outlet, Route, Routes } from 'react-router-dom'
import { HomePage } from './pages/page'

function App() {
  return (
    <React.Fragment>
      <Routes>
        <Route path="/" element={<Outlet />}>
          <Route index element={<HomePage />} />
        </Route>
      </Routes>
    </React.Fragment>
  )
}

export default App
