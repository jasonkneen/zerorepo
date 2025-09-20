import React, { useState, useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import LandingPage from "./components/LandingPage";
import GenerationPage from "./components/GenerationPage";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "http://localhost:8001";
const API = `${BACKEND_URL.replace(/\/$/, "")}/api`;

function App() {
  const [isDarkMode, setIsDarkMode] = useState(true);

  // Initialize API connection check
  useEffect(() => {
    const checkAPI = async () => {
      try {
        const response = await axios.get(`${API}/`);
        console.log("ZeroRepo API:", response.data.message);
      } catch (e) {
        console.error("API connection error:", e);
      }
    };
    checkAPI();
  }, []);

  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route 
            path="/" 
            element={
              <LandingPage 
                isDarkMode={isDarkMode} 
                setIsDarkMode={setIsDarkMode} 
              />
            } 
          />
          <Route 
            path="/generate" 
            element={
              <GenerationPage 
                isDarkMode={isDarkMode} 
                setIsDarkMode={setIsDarkMode} 
              />
            } 
          />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
