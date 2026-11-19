
import {
  LayoutDashboard,
  Users,
  BrainCircuit,
  ChartNoAxesCombined,
  Settings,
  ShieldCheck,
  PanelLeftClose,
} from "lucide-react";

interface SidebarProps {
  activePage: string;
  setActivePage: (page: string) => void;
  onToggle: () => void;
}

const Sidebar = ({
  activePage,
  setActivePage,
  onToggle,
}: SidebarProps) => {
  const menuItems = [
    { name: "Dashboard", icon: LayoutDashboard },
    { name: "Customers", icon: Users },
    { name: "Churn Prediction", icon: BrainCircuit },
    { name: "Analytics", icon: ChartNoAxesCombined },
  ];

  return (
    <aside className="sidebar">
      <div className="brand">
        <ShieldCheck size={30} />
        <span>ChurnGuard</span>

        <button
          className="nav-toggle"
          onClick={onToggle}
          title="Hide navigation"
          aria-label="Hide navigation"
        >
          <PanelLeftClose size={19} />
        </button>
      </div>

      <p className="menu-label">MAIN MENU</p>

      <nav>
        {menuItems.map((item) => {
          const Icon = item.icon;

          return (
            <div
              key={item.name}
              className={`nav-item ${
                activePage === item.name ? "active" : ""
              }`}
              onClick={() => setActivePage(item.name)}
            >
              <Icon size={19} />
              <span>{item.name}</span>
            </div>
          );
        })}
      </nav>

      <div className="sidebar-bottom">
        <Settings size={19} />
        <span>Settings</span>
      </div>
    </aside>
  );
};

export default Sidebar;
