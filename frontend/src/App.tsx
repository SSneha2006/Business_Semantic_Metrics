
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Datasets from "./pages/Datasets";
import Sidebar from "./components/Sidebar";
import Header from "./components/Header";
import Dashboard from "./pages/Dashboard";
import ModulePage from "./pages/ModulePage";
import "./App.css";

function App() {
  return (
    <BrowserRouter>
      <div className="app-layout">
        <Sidebar />

        <main className="main-content">
          <Header />

          <div className="page-content">
            <Routes>
              <Route path="/" element={<Dashboard />} />

              <Route path="/datasets" element={<Datasets />} />
              <Route
                path="/metrics"
                element={
                  <ModulePage
                    title="Semantic Metrics"
                    description="Define and manage consistent business metrics."
                  />
                }
              />

              <Route
                path="/conflicts"
                element={
                  <ModulePage
                    title="Metric Conflicts"
                    description="Identify and resolve conflicting metric definitions."
                  />
                }
              />

   
              <Route
                path="/users"
                element={
                  <ModulePage
                    title="User Management"
                    description="Manage workspace users and permissions."
                  />
                }
              />

              <Route
                path="/settings"
                element={
                  <ModulePage
                    title="Settings"
                    description="Manage your workspace settings."
                  />
                }
              />

              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </div>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
