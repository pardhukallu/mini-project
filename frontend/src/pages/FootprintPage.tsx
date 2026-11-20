import { useState } from "react";
import UsernameScannerComponent from "../components/scans/UsernameScannerComponent";
import DomainAuditComponent from "../components/scans/DomainAuditComponent";

type FootprintTab = "username" | "domain";

interface FootprintPageProps {
  initialTab?: FootprintTab;
}

export default function FootprintPage({ initialTab = "username" }: FootprintPageProps) {
  const [activeTab, setActiveTab] = useState<FootprintTab>(initialTab);

  const tabs: { id: FootprintTab; label: string }[] = [
    { id: "username", label: "Username OSINT" },
    { id: "domain", label: "Domain Security" },
  ];

  return (
    <div className="p-6 space-y-6">
      {/* Page header */}
      <div>
        <h1 className="text-xl font-semibold text-slate-100">Digital Footprint</h1>
        <p className="text-sm text-slate-400 mt-1">
          Analyze your public digital presence and email domain security posture.
        </p>
      </div>

      {/* Tab bar */}
      <div className="flex gap-1 p-1 bg-slate-800/60 border border-slate-700/50 rounded-lg w-fit">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
              activeTab === tab.id
                ? "bg-teal-600 text-white"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Panel */}
      <div className="p-6 bg-slate-800/40 border border-slate-700/50 rounded-xl">
        {activeTab === "username" ? <UsernameScannerComponent /> : <DomainAuditComponent />}
      </div>
    </div>
  );
}
