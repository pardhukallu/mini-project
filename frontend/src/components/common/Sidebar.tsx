import React from 'react';
import { LayoutDashboard, Mail, Globe2, Puzzle, Gauge, Sparkles, FileText, ShieldCheck } from 'lucide-react';

interface SidebarProps { currentTab: string; onTabChange: (tab: string) => void; }

export const Sidebar: React.FC<SidebarProps> = ({ currentTab, onTabChange }) => {
  const groups = [
    { title: 'WORKSPACE', items: [
      { id: 'dashboard', label: 'Overview', icon: LayoutDashboard },
    ]},
    { title: 'MONITORING', items: [
      { id: 'breaches', label: 'Email breaches', icon: Mail },
      { id: 'footprint', label: 'Digital footprint', icon: Globe2 },
      { id: 'permissions', label: 'Browser privacy', icon: Puzzle },
    ]},
    { title: 'INTELLIGENCE', items: [
      { id: 'scoring', label: 'Evidence score', icon: Gauge },
      { id: 'remediation', label: 'Recommendations', icon: Sparkles },
      { id: 'reports', label: 'Audit reports', icon: FileText },
    ]},
  ];
  return <aside className="sw-sidebar">
    <div className="sw-side-brand"><div className="sw-brand-mark"><ShieldCheck size={20}/></div><div><b>shadow<span>watch</span></b><small>PERSONAL SECURITY</small></div></div>
    <div className="sw-side-nav">{groups.map(group => <div className="sw-nav-group" key={group.title}><div className="sw-nav-label">{group.title}</div>{group.items.map(item => {
      const Icon = item.icon; const active = currentTab === item.id;
      return <button key={item.id} onClick={() => onTabChange(item.id)} className={`sw-nav-item ${active ? 'active' : ''}`}><Icon size={17}/><span>{item.label}</span>{active && <i/>}</button>;
    })}</div>)}</div>
    <div className="sw-side-bottom"><div className="sw-side-orb"><div/><div/><div/></div><div className="sw-side-bottom-copy"><b>Your privacy matters.</b><span>Scan only what you choose.</span></div></div>
  </aside>;
};
