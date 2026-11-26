
import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  Database,
  Calculator,
  GitCompare,
  Bot,
  Users,
  Settings,
  Layers,
} from "lucide-react";

const menuItems = [
  { name: "Dashboard", path: "/", icon: LayoutDashboard },
  { name: "Datasets", path: "/datasets", icon: Database },
  { name: "Semantic Metrics", path: "/metrics", icon: Calculator },
  { name: "Metric Conflicts", path: "/conflicts", icon: GitCompare },
  { name: "User Management", path: "/users", icon: Users },
];

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-icon">
          <Layers size={24} />
        </div>
        <div>
          <h2>Semantic BI</h2>
          <span>METRICS PLATFORM</span>
        </div>
      </div>

      <p className="menu-label">WORKSPACE</p>

      <nav>
        {menuItems.map((item) => {
          const Icon = item.icon;

          return (
            <NavLink
              to={item.path}
              key={item.path}
              end={item.path === "/"}
              className={({ isActive }) =>
                `nav-item ${isActive ? "active" : ""}`
              }
            >
              <Icon size={19} />
              <span>{item.name}</span>
            </NavLink>
          );
        })}
      </nav>

      <div className="sidebar-bottom">
        <NavLink to="/settings" className="nav-item">
          <Settings size={19} />
          <span>Settings</span>
        </NavLink>

        <div className="workspace-user">
          <div className="avatar">SS</div>
          <div>
            <strong>Subha Sneha</strong>
            <small>Workspace Admin</small>
          </div>
        </div>
      </div>
    </aside>
  );
}
