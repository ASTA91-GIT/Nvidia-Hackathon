import React, { useState } from 'react';
import { X, Zap, Database, Cpu, WifiOff, AlertTriangle, ArrowRight } from 'lucide-react';
import type { Scenario } from '../types';

interface SimulateModalProps {
  isOpen: boolean;
  onClose: () => void;
  scenarios: Scenario[];
  onSimulate: (scenarioId: string, autoInvestigate: boolean) => Promise<void>;
}

export const SimulateModal: React.FC<SimulateModalProps> = ({
  isOpen,
  onClose,
  scenarios,
  onSimulate,
}) => {
  const [selectedScenario, setSelectedScenario] = useState<string>('scenario_db_regression');
  const [autoInvestigate, setAutoInvestigate] = useState<boolean>(true);
  const [loading, setLoading] = useState<boolean>(false);

  if (!isOpen) return null;

  const handleTrigger = async () => {
    setLoading(true);
    try {
      await onSimulate(selectedScenario, autoInvestigate);
      onClose();
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getScenarioIcon = (id: string) => {
    if (id.includes('db')) return <Database className="w-5 h-5 text-infra-rose" />;
    if (id.includes('memory')) return <Cpu className="w-5 h-5 text-infra-amber" />;
    return <WifiOff className="w-5 h-5 text-infra-cyan" />;
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fade-in">
      <div className="glass-panel w-full max-w-xl rounded-2xl border border-cyber-700 bg-cyber-950 p-6 shadow-2xl relative">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-white p-1 rounded-lg hover:bg-cyber-800 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Modal Header */}
        <div className="flex items-center space-x-3 mb-6">
          <div className="p-2.5 rounded-xl bg-infra-rose/15 border border-infra-rose/40 text-infra-rose">
            <Zap className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white font-mono">
              Inject Production Incident Simulation
            </h3>
            <p className="text-xs text-slate-400 font-sans">
              Select an architectural failure scenario to simulate in the microservices environment.
            </p>
          </div>
        </div>

        {/* Scenarios List */}
        <div className="space-y-3 mb-6">
          {scenarios.map((sc) => {
            const isSelected = selectedScenario === sc.id;
            return (
              <div
                key={sc.id}
                onClick={() => setSelectedScenario(sc.id)}
                className={`p-4 rounded-xl border cursor-pointer transition-all ${
                  isSelected
                    ? 'border-infra-rose/80 bg-cyber-900/90 shadow-md shadow-rose-950/30'
                    : 'border-cyber-800 bg-cyber-950/60 hover:border-cyber-700 hover:bg-cyber-900/40'
                }`}
              >
                <div className="flex items-start space-x-3">
                  <div className="p-2 rounded-lg bg-cyber-950 border border-cyber-800 shrink-0">
                    {getScenarioIcon(sc.id)}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <h4 className="text-xs font-bold text-white font-mono">{sc.title}</h4>
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-rose-950/60 text-infra-rose border border-rose-900/60 font-semibold">
                        {sc.severity}
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-300 font-sans leading-relaxed">
                      {sc.description}
                    </p>
                    <span className="text-[10px] font-mono text-slate-500 mt-1 block">
                      Target Service: <strong className="text-slate-400">{sc.service}</strong>
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Options */}
        <div className="p-3 bg-cyber-900/60 rounded-xl border border-cyber-800 flex items-center justify-between mb-6 text-xs font-mono">
          <div>
            <span className="font-bold text-white block">Auto-Dispatch Multi-Agent Investigation</span>
            <span className="text-[10px] text-slate-400 font-sans">
              Incident Commander coordinates log, metrics, code, and root cause agents immediately.
            </span>
          </div>
          <input
            type="checkbox"
            checked={autoInvestigate}
            onChange={(e) => setAutoInvestigate(e.target.checked)}
            className="w-4 h-4 accent-infra-emerald cursor-pointer"
          />
        </div>

        {/* Modal Action Buttons */}
        <div className="flex items-center justify-end space-x-3">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg text-xs font-mono text-slate-400 hover:text-white transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleTrigger}
            disabled={loading}
            className="flex items-center space-x-2 px-5 py-2.5 rounded-lg bg-gradient-to-r from-infra-rose to-orange-600 hover:from-rose-600 hover:to-orange-700 text-white font-mono text-xs font-bold shadow-lg shadow-rose-950/50 active:scale-95 transition-all"
          >
            <span>{loading ? 'Simulating...' : 'Simulate & Trigger Incident'}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};
