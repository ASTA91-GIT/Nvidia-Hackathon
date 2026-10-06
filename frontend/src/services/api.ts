import type { Incident, SystemHealth, Scenario, IncidentReport, Evidence, AgentRun, TimelineEvent, RemediationAction } from '../types';

const API_BASE = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';
const WS_BASE = API_BASE.replace(/^http/, 'ws');

export const api = {
  async getSystemHealth(): Promise<SystemHealth> {
    const res = await fetch(`${API_BASE}/api/system/health`);
    if (!res.ok) throw new Error('Failed to fetch system health');
    return res.json();
  },

  async getScenarios(): Promise<Scenario[]> {
    const res = await fetch(`${API_BASE}/api/scenarios`);
    if (!res.ok) throw new Error('Failed to fetch scenarios');
    return res.json();
  },

  async getIncidents(): Promise<Incident[]> {
    const res = await fetch(`${API_BASE}/api/incidents`);
    if (!res.ok) throw new Error('Failed to fetch incidents');
    return res.json();
  },

  async getIncident(id: string): Promise<Incident> {
    const res = await fetch(`${API_BASE}/api/incidents/${id}`);
    if (!res.ok) throw new Error(`Failed to fetch incident ${id}`);
    return res.json();
  },

  async simulateIncident(scenario_id: string, auto_investigate: boolean = true): Promise<{ incident_id: string; title: string }> {
    const res = await fetch(`${API_BASE}/api/simulate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ scenario_id, auto_investigate }),
    });
    if (!res.ok) throw new Error('Failed to trigger simulation');
    return res.json();
  },

  async startInvestigation(incidentId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/api/incidents/${incidentId}/investigate`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error('Failed to start investigation');
    return res.json();
  },

  async getEvidence(incidentId: string): Promise<Evidence[]> {
    const res = await fetch(`${API_BASE}/api/incidents/${incidentId}/evidence`);
    if (!res.ok) throw new Error('Failed to fetch evidence');
    return res.json();
  },

  async getAgents(incidentId: string): Promise<AgentRun[]> {
    const res = await fetch(`${API_BASE}/api/incidents/${incidentId}/agents`);
    if (!res.ok) throw new Error('Failed to fetch agents');
    return res.json();
  },

  async getTimeline(incidentId: string): Promise<TimelineEvent[]> {
    const res = await fetch(`${API_BASE}/api/incidents/${incidentId}/timeline`);
    if (!res.ok) throw new Error('Failed to fetch timeline');
    return res.json();
  },

  async remediate(incidentId: string, actionType: string, targetService: string, parameters?: any): Promise<RemediationAction> {
    const res = await fetch(`${API_BASE}/api/incidents/${incidentId}/remediate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action_type: actionType, target_service: targetService, parameters }),
    });
    if (!res.ok) throw new Error('Failed to execute remediation');
    return res.json();
  },

  async getReport(incidentId: string): Promise<IncidentReport> {
    const res = await fetch(`${API_BASE}/api/incidents/${incidentId}/report`);
    if (!res.ok) throw new Error('Failed to fetch report');
    return res.json();
  },
};

export function connectWebSocket(incidentId: string = 'global', onMessage: (event: any) => void): WebSocket {
  const url = incidentId === 'global' ? `${WS_BASE}/ws` : `${WS_BASE}/ws/investigation/${incidentId}`;
  const socket = new WebSocket(url);

  socket.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage(data);
    } catch (e) {
      console.warn('Failed to parse websocket message:', e);
    }
  };

  socket.onerror = (err) => {
    console.error('WebSocket connection error:', err);
  };

  return socket;
}
