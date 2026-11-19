
import { useState } from "react";
import { PanelLeftOpen } from "lucide-react";

import Sidebar from "./components/Sidebar";
import Dashboard from "./pages/Dashboard";
import CustomerPrediction from "./pages/CustomerPrediction";
import Customers from "./pages/Customers";
import Analytics from "./pages/Analytics";

import "./App.css";

function App() {
  const [activePage, setActivePage] = useState("Dashboard");
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  return (
    <div className={`app-layout ${!isSidebarOpen ? "sidebar-hidden" : ""}`}>
      {isSidebarOpen && (
        <Sidebar
          activePage={activePage}
          setActivePage={setActivePage}
          onToggle={() => setIsSidebarOpen(false)}
        />
      )}

      {!isSidebarOpen && (
        <button
          className="sidebar-reopen"
          onClick={() => setIsSidebarOpen(true)}
          title="Show navigation"
          aria-label="Show navigation"
        >
          <PanelLeftOpen size={21} />
        </button>
      )}

      {activePage === "Dashboard" && <Dashboard />}
      {activePage === "Churn Prediction" && <CustomerPrediction />}
      {activePage === "Customers" && <Customers />}
      {activePage === "Analytics" && <Analytics />}
    </div>
  );
}

export default App;
