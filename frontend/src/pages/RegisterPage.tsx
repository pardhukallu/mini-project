import React from 'react';
import { Shield } from 'lucide-react';
import { RegisterForm } from '../components/auth/RegisterForm';

interface RegisterPageProps {
  onToggleToLogin: () => void;
}

export const RegisterPage: React.FC<RegisterPageProps> = ({ onToggleToLogin }) => {
  return (
    <div className="min-h-screen bg-navy-950 flex flex-col justify-center items-center p-6 relative">
      <div className="absolute inset-0 pointer-events-none bg-[radial-gradient(ellipse_at_70%_20%,rgba(55,105,205,0.22),transparent_42%)]"></div>

      {/* Brand Header */}
      <div className="flex items-center space-x-3 mb-8 z-10">
        <div className="w-10 h-10 rounded bg-teal-500/10 border border-teal-500/30 flex items-center justify-center text-teal-400">
          <Shield className="w-6 h-6 text-teal-400" />
        </div>
        <div className="text-left">
          <h1 className="font-mono font-bold tracking-wider text-slate-100 text-lg">
            SHADOW<span className="text-teal-400">WATCH</span>
          </h1>
          <p className="text-[11px] font-mono text-slate-400">
            Personal Data Exposure & Privacy Intelligence
          </p>
        </div>
      </div>

      {/* Form Card */}
      <div className="z-10 w-full flex justify-center">
        <RegisterForm onToggleToLogin={onToggleToLogin} />
      </div>

      {/* Footer */}
      <div className="mt-8 text-center text-[11px] font-mono text-slate-500 z-10">
        <span>Account credentials are protected with Argon2id password hashing.</span>
      </div>
    </div>
  );
};
