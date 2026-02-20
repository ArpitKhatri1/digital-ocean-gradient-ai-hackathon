import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar";
import Header from "../header/Header";
const SidebarLayout = () => {
  return (
    // make the layout span the full viewport and use column flex so header stays on top
    <div className="min-h-screen min-w-screen flex flex-col">
      <Header />

      {/* main area: sidebar + page content; flex-1 so it fills remaining height */}
      <div className="flex flex-1 w-full">
        <Sidebar />
        <Outlet />
      </div>
    </div>
  );
};

export default SidebarLayout;
