import { type LucideIcon } from "lucide-react";
import { Box } from "lucide-react";
const Header = () => {
  return (
    <div className="flex justify-between m-3 px-5">
      <div></div>
      <div></div>
      <div>
        <HeaderItem Icon={Box} />
      </div>
    </div>
  );
};

type HeaderProps = {
  Icon: LucideIcon;
};

const HeaderItem = ({ Icon }: HeaderProps) => {
  return (
    <div className=" h-9 w-9 rounded-lg bg-red-100 flex items-center justify-center ">
      <Icon size={22} />
    </div>
  );
};

export default Header;
