import React, { useState, useEffect, useCallback } from 'react';
import { Navbar } from './components/Navbar';
import { Dashboard } from './components/Dashboard';
import { InvestigationView } from './components/InvestigationView';
import { SimulateModal } from './components/SimulateModal';
import { api, connectWebSocket } from './services/api';
import type { Incident, SystemHealth, Scenario, AgentRun, Evidence, MetricSnapshot, LogEvent, IncidentReport } from './types';

export function App() {
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [activeView, setActiveView] = useState<string>('dashboard');
  const [selectedIncidentId, setSelectedIncidentId] = useState<string | null>(null);
  
  // Selected incident deep state
  const [currentIncident, setCurrentIncident] = useState<Incident | null>(null);
  const [agentRuns, setAgentRuns] = useState<AgentRun[]>([]);
  const [evidences, setEvidences] = useState<Evidence[]>([]);
  const [metrics, setMetrics] = useState<MetricSnapshot[]>([]);
  const [logs, setLogs] = useState<LogEvent[]>([]);
  const [report, setReport] = useState<IncidentReport | null>(null);

  const [isSimulateModalOpen, setIsSimulateModalOpen] = useState(false);

  // Load initial health & scenarios
  const refreshSystem = useCallback(async () => {
    try {
      const [h, sc, incs] = await Promise.all([
        api.getSystemHealth().catch(() => null),
        api.getScenarios().catch(() => []),
        api.getIncidents().catch(() => []),
      ]);
      if (h) setHealth(h);
      if (sc) setScenarios(sc);
      if (incs) setIncidents(incs);
    } catch (e) {
      console.error('System refresh failed:', e);
    }
  }, []);

  useEffect(() => {
    refreshSystem();
    const interval = setInterval(refreshSystem, 5000);
    return () => clearInterval(interval);
  }, [refreshSystem]);

  // Load selected incident details
  const loadIncidentDetails = useCallback(async (id: string) => {
    try {
      const inc = await api.getIncident(id);
      setCurrentIncident(inc);
      setMetrics(inc.metrics || []);
      setLogs(inc.logs || []);
      setReport(inc.report || null);

      const [agents, evis] = await Promise.all([
        api.getAgents(id).catch(() => []),
        api.getEvidence(id).catch(() => []),
      ]);
      setAgentRuns(agents);
      setEvidences(evis);
    } catch (e) {
      console.error(`Failed to load incident ${id}:`, e);
    }
  }, []);

  useEffect(() => {
    if (selectedIncidentId) {
      loadIncidentDetails(selectedIncidentId);
    }
  }, [selectedIncidentId, loadIncidentDetails]);

  // Real-time WebSocket connection
  useEffect(() => {
    const ws = connectWebSocket(selectedIncidentId || 'global', (message) => {
      console.log('WS Event received:', message);
      const { event, data } = message;

      if (event === 'incident_triggered') {
        refreshSystem();
        if (data?.id) {
          setSelectedIncidentId(data.id);
          setActiveView('investigation');
        }
      } else if (event === 'agent_status_change' && selectedIncidentId) {
        loadIncidentDetails(selectedIncidentId);
      } else if (event === 'phase_changed' || event === 'remediation_executed' || event === 'investigation_completed') {
        if (selectedIncidentId) {
          loadIncidentDetails(selectedIncidentId);
        }
        refreshSystem();
      }
    });

    return () => {
      ws.close();
    };
  }, [selectedIncidentId, refreshSystem, loadIncidentDetails]);

  // Actions
  const handleSelectIncident = (id: string) => {
    setSelectedIncidentId(id);
    setActiveView('investigation');
  };

  const handleSimulate = async (scenarioId: string, autoInvestigate: boolean) => {
    const res = await api.simulateIncident(scenarioId, autoInvestigate);
    setSelectedIncidentId(res.incident_id);
    setActiveView('investigation');
    await refreshSystem();
  };

  const handleStartInvestigation = async () => {
    if (!selectedIncidentId) return;
    await api.startInvestigation(selectedIncidentId);
    await loadIncidentDetails(selectedIncidentId);
  };

  const handleExecuteRemediation = async (actionType: string, targetService: string) => {
    if (!selectedIncidentId) throw new Error('No incident selected');
    const res = await api.remediate(selectedIncidentId, actionType, targetService);
    await loadIncidentDetails(selectedIncidentId);
    await refreshSystem();
    return res;
  };

  return (
    <div className="min-h-screen bg-cyber-950 text-slate-100 flex flex-col font-sans">
      <Navbar
        health={health}
        onOpenSimulateModal={() => setIsSimulateModalOpen(true)}
        activeView={activeView}
        setActiveView={setActiveView}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {activeView === 'dashboard' && (
          <Dashboard
            health={health}
            incidents={incidents}
            onSelectIncident={handleSelectIncident}
            onOpenSimulateModal={() => setIsSimulateModalOpen(true)}
          />
        )}

        {activeView === 'incidents' && (
          <Dashboard
            health={health}
            incidents={incidents}
            onSelectIncident={handleSelectIncident}
            onOpenSimulateModal={() => setIsSimulateModalOpen(true)}
          />
        )}

        {activeView === 'investigation' && currentIncident && (
          <InvestigationView
            incident={currentIncident}
            agentRuns={agentRuns}
            evidences={evidences}
            metrics={metrics}
            logs={logs}
            report={report}
            onBack={() => setActiveView('dashboard')}
            onStartInvestigation={handleStartInvestigation}
            onExecuteRemediation={handleExecuteRemediation}
          />
        )}
      </main>

      <SimulateModal
        isOpen={isSimulateModalOpen}
        onClose={() => setIsSimulateModalOpen(false)}
        scenarios={scenarios}
        onSimulate={handleSimulate}
      />

      {/* Cyberpunk Footer */}
      <footer className="border-t border-cyber-800/80 bg-cyber-950/90 py-4 text-center text-xs font-mono text-slate-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>INCIDENTZERO • Autonomous AI Incident Commander</span>
          <span>NVIDIA Nemotron • Nebius Token Factory • Global AI Hackathon 2025</span>
        </div>
      </footer>
    </div>
  );
}

export default App;
