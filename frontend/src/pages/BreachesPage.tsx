import React from 'react';
import { Mail } from 'lucide-react';
import { EmailBreachScanner } from '../components/scans/EmailBreachScanner';

export const BreachesPage: React.FC = () => <div className="flex-1 p-8 max-w-6xl mx-auto w-full space-y-7">
  <header className="sw-page-header"><div><p className="sw-eyebrow">EXPOSURE AUDIT</p><h1 className="text-3xl font-semibold text-white mt-2">Email breach check</h1><p className="text-sm text-slate-400 mt-2">Find out whether an email address appears in known public data breaches.</p></div><div className="sw-icon-tile"><Mail size={22}/></div></header>
  <EmailBreachScanner />
</div>;
