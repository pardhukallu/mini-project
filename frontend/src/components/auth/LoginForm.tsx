import React, { useState } from 'react';
import { Eye, EyeOff, Lock, Mail, ShieldAlert, ArrowRight } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

interface LoginFormProps {
  onToggleToRegister: () => void;
}

export const LoginForm: React.FC<LoginFormProps> = ({ onToggleToRegister }) => {
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      setErrorMessage('Please enter both email and password.');
      return;
    }

    setIsSubmitting(true);
    setErrorMessage(null);

    try {
      await login(email, password);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Invalid credentials';
      setErrorMessage(msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="w-full max-w-md bg-navy-850 border border-navy-700/80 rounded-lg p-7 shadow-2xl">
      {/* Header */}
      <div className="mb-6">
        <div className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded bg-teal-500/10 text-teal-400 border border-teal-500/20 text-xs font-mono mb-3">
          <Lock className="w-3.5 h-3.5" />
          <span>AUTHENTICATED ACCESS ONLY</span>
        </div>
        <h2 className="text-xl font-semibold text-slate-100 font-mono tracking-tight">
          Operator Login
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Access your private digital exposure dashboard and telemetry.
        </p>
      </div>

      {/* Error Alert */}
      {errorMessage && (
        <div className="mb-5 p-3 rounded bg-red-950/50 border border-red-500/30 text-red-300 text-xs font-mono flex items-start space-x-2.5">
          <ShieldAlert className="w-4 h-4 text-red-400 mt-0.5 shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-xs font-mono text-slate-400 mb-1.5 uppercase">
            Account Email
          </label>
          <div className="relative">
            <Mail className="w-4 h-4 text-slate-500 absolute left-3 top-3" />
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="analyst@shadowwatch.io"
              required
              className="w-full bg-navy-900 border border-navy-700 rounded px-9 py-2.5 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-teal-500 font-mono transition"
            />
          </div>
        </div>

        <div>
          <label className="block text-xs font-mono text-slate-400 mb-1.5 uppercase">
            Master Password
          </label>
          <div className="relative">
            <Lock className="w-4 h-4 text-slate-500 absolute left-3 top-3" />
            <input
              type={showPassword ? 'text' : 'password'}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••••••"
              required
              className="w-full bg-navy-900 border border-navy-700 rounded px-9 py-2.5 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-teal-500 font-mono transition"
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-3 text-slate-500 hover:text-slate-300"
            >
              {showPassword ? (
                <EyeOff className="w-4 h-4" />
              ) : (
                <Eye className="w-4 h-4" />
              )}
            </button>
          </div>
        </div>

        <button
          type="submit"
          disabled={isSubmitting}
          className="w-full mt-2 bg-teal-500 hover:bg-teal-400 disabled:bg-teal-800 disabled:cursor-not-allowed text-navy-950 font-semibold font-mono text-xs py-3 rounded transition duration-150 flex items-center justify-center space-x-2"
        >
          {isSubmitting ? (
            <span>VERIFYING CREDENTIALS...</span>
          ) : (
            <>
              <span>ESTABLISH SECURE SESSION</span>
              <ArrowRight className="w-4 h-4" />
            </>
          )}
        </button>
      </form>

      {/* Switch to Register */}
      <div className="mt-6 pt-5 border-t border-navy-800 flex items-center justify-between text-xs font-mono">
        <span className="text-slate-500">Need a monitor account?</span>
        <button
          onClick={onToggleToRegister}
          className="text-teal-400 hover:text-teal-300 underline underline-offset-4"
        >
          Register New Account
        </button>
      </div>
    </div>
  );
};
