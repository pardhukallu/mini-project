import React from 'react';
import { LogOut, ShieldCheck, Activity, UserRound } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export const Navbar: React.FC = () => {
  const { user, logout } = useAuth();
  return <header className="sw-topbar">
    <div className="sw-mobile-brand"><ShieldCheck size={19}/><b>shadow<span>watch</span></b></div>
    <div className="sw-topbar-status"><span className="sw-live-dot"/><Activity size={15}/><span>All systems operational</span></div>
    <div className="sw-topbar-right">{user && <div className="sw-user-chip"><UserRound size={15}/><span>{user.email}</span><i>SECURE</i></div>}<button onClick={logout} className="sw-logout"><LogOut size={15}/><span>Sign out</span></button></div>
  </header>;
};
