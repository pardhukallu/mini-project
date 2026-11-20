import React, { useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { DashboardPage } from './pages/DashboardPage';
import { BreachesPage } from './pages/BreachesPage';
import FootprintPage from './pages/FootprintPage';
import { Navbar } from './components/common/Navbar';
import { Sidebar } from './components/common/Sidebar';
import { Shield } from 'lucide-react';
import IntelligencePage from './pages/IntelligencePage';

const AppContent: React.FC = () => {
  const { isAuthenticated, isLoading } = useAuth();
  const [authView, setAuthView] = useState<'login' | 'register'>('login');
  const [currentTab, setCurrentTab] = useState<string>('dashboard');

  if (isLoading) {
    return (
      <div className="min-h-screen bg-navy-950 flex flex-col items-center justify-center space-y-4">
        <div className="w-12 h-12 rounded-lg bg-teal-500/10 border border-teal-500/30 flex items-center justify-center text-teal-400 animate-pulse">
          <Shield className="w-6 h-6 text-teal-400" />
        </div>
        <span className="text-xs font-mono text-slate-400 tracking-wider">
          AUTHENTICATING OPERATOR...
        </span>
      </div>
    );
  }

  if (!isAuthenticated) {
    return authView === 'login' ? (
      <LoginPage onToggleToRegister={() => setAuthView('register')} />
    ) : (
      <RegisterPage onToggleToLogin={() => setAuthView('login')} />
    );
  }

  return (
    <div className="sw-app-shell">
      <Navbar />
      <div className="sw-app-body">
        <Sidebar currentTab={currentTab} onTabChange={setCurrentTab} />
        <main className="sw-main">
          {currentTab === 'dashboard' && <DashboardPage />}
          {currentTab === 'breaches' && <BreachesPage />}
          {currentTab === 'footprint' && <FootprintPage initialTab="username" />}
          {['permissions','scoring','remediation','reports'].includes(currentTab) && <IntelligencePage tab={currentTab} />}
        </main>
      </div>
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
};

export default App;
