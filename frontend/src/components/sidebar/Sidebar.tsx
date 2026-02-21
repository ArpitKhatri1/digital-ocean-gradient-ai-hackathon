import { House, Settings, CirclePile, Map } from "lucide-react";
import { type LucideIcon } from "lucide-react";
import { Link } from "react-router-dom";

const Sidebar = () => {
  return (
    <div className="ml-4 mr-4 pb-10 flex flex-col">
      <div className=" flex flex-col gap-5 ">
        <Link to="/">
          <div>
            <SidebarItem Icon={House} />
          </div>
        </Link>
        <Link to="/inventory">
          <div>
            <SidebarItem Icon={CirclePile} />
          </div>
        </Link>
        <Link to="/map">
          <div>
            <SidebarItem Icon={Map} />
          </div>
        </Link>
      </div>
      <div className="mt-auto">
        <SidebarItem Icon={Settings} />
      </div>
    </div>
  );
};

type SidebarProps = {
  Icon: LucideIcon;
};

const SidebarItem = ({ Icon }: SidebarProps) => {
  return (
    <div className=" h-10 w-10 rounded-lg bg-red-100 flex items-center justify-center ">
      <Icon size={22} />
    </div>
  );
};

export default Sidebar;
