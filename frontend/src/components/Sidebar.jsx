import React from 'react';
import { LayoutDashboard, Compass, AlertOctagon, Ship, FileText, Settings, HelpCircle } from 'lucide-react';

export default function Sidebar({ activeTab, onSelectTab }) {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'analysis', label: 'Analysis', icon: Compass },
    { id: 'incidents', label: 'Incidents', icon: AlertOctagon },
    { id: 'vessels', label: 'Vessels', icon: Ship },
    { id: 'reports', label: 'Reports', icon: FileText },
    { id: 'settings', label: 'Settings', icon: Settings },
    { id: 'help', label: 'Help', icon: HelpCircle },
  ];

  return (
    <aside className="left-nav-rail">
      {navItems.map((item) => {
        const Icon = item.icon;
        const isActive = activeTab === item.id;
        return (
          <button 
            key={item.id}
            className={`nav-item-btn ${isActive ? 'active' : ''}`}
            onClick={() => onSelectTab(item.id)}
            title={item.label}
          >
            <Icon size={20} />
            <span>{item.label}</span>
          </button>
        );
      })}
    </aside>
  );
}
