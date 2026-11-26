import { Bell, Search, ChevronDown } from "lucide-react";

export default function Header() {
  return (
    <header className="top-header">
      <div>
        <h2>Business Intelligence</h2>
        <p>Monitor and manage your business metrics</p>
      </div>

      <div className="header-actions">
        <div className="search-box">
          <Search size={18} />
          <input placeholder="Search anything..." />
        </div>

        <button className="icon-button">
          <Bell size={20} />
        </button>

        <button className="profile-button">
          SS <ChevronDown size={16} />
        </button>
      </div>
    </header>
  );
}