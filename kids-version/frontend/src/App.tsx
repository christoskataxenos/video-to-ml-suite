/**
 * PolyMind — App Entry Point.
 * Routing: "/" -> ParentDashboard, "/kids" -> KidsHome.
 */

import { BrowserRouter, Routes, Route } from "react-router-dom";
import ParentDashboard from "./pages/ParentDashboard";
import KidsHome from "./pages/KidsHome";
import "./index.css";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<ParentDashboard />} />
        <Route path="/kids" element={<KidsHome />} />
      </Routes>
    </BrowserRouter>
  );
}
