import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Dashboard from "./components/dashboard/Dashboard";
import SidebarLayout from "./components/sidebar/SidebarLayout";
import Medicine from "./components/medicine/Medicine";
import MapTransfer from "./components/map/MapTransfer";
import Inventory from "./components/inventory/Inventory";
function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<SidebarLayout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/medicine/:id" element={<Medicine />} />
          <Route path="/map" element={<MapTransfer />} />
          <Route path="/inventory" element={<Inventory />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
