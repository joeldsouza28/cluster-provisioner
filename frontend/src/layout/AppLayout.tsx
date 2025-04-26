import { SidebarProvider, useSidebar } from "../context/SidebarContext";
import { Outlet } from "react-router";
import AppHeader from "./AppHeader";
import Backdrop from "./Backdrop";
import AppSidebar from "./AppSidebar";
import { useEffect, useState } from "react";
import { checkSession } from "../services";

const LayoutContent: React.FC = () => {
  const { isExpanded, isHovered, isMobileOpen } = useSidebar();
  const [name, setName] = useState("");
  const [avatarUrl, setAvatarUrl] = useState("");

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await checkSession();
        const data = await res.json();
        let user = data["user"]
        setAvatarUrl(user["avatar_url"]);
        setName(user["name"]);
      } catch (error) {
        console.error('Error fetching data:', error);
        window.location.href = "/login"
      }
    };
    fetchData();
  }, [])

  return (
    <div className="min-h-screen xl:flex">
      <div>
        <AppSidebar />
        <Backdrop />
      </div>
      <div
        className={`flex-1 transition-all duration-300 ease-in-out ${isExpanded || isHovered ? "lg:ml-[290px]" : "lg:ml-[90px]"
          } ${isMobileOpen ? "ml-0" : ""}`}
      >

        
        <AppHeader avatar_url={avatarUrl} name={name} />
        <div className="p-4 mx-auto max-w-(--breakpoint-2xl) md:p-6">
          <Outlet />
        </div>
      </div>
    </div>
  );
};

const AppLayout: React.FC = () => {
  
  

  return (
    <SidebarProvider>
      <LayoutContent />
    </SidebarProvider>
  );
};

export default AppLayout;
