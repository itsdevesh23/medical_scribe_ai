import { useState, useEffect } from 'react';
import axios from 'axios';
import { Clock, Eye, AlertCircle, Loader2 } from 'lucide-react';

const BASE_URL = `${window.location.protocol}//${window.location.hostname}:8000`;

export default function History({ onViewSession }) {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSessions = async () => {
      try {
        const res = await axios.get(`${BASE_URL}/api/sessions`);
        setSessions(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchSessions();
  }, []);

  const getStatusBadge = (status) => {
    switch (status) {
      case 'completed': return <div className="badge badge-success gap-1">Completed</div>;
      case 'processing': return <div className="badge badge-info gap-1"><Loader2 size={12} className="animate-spin" /> Processing</div>;
      case 'failed': return <div className="badge badge-error gap-1"><AlertCircle size={12} /> Failed</div>;
      default: return <div className="badge badge-ghost">{status}</div>;
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-[50vh]">
        <Loader2 className="animate-spin text-primary" size={48} />
      </div>
    );
  }

  return (
    <div className="card bg-base-100 shadow-xl border border-base-200 animate-in fade-in duration-500">
      <div className="card-body">
        <h2 className="card-title text-2xl mb-6">Session History</h2>
        
        {sessions.length === 0 ? (
          <div className="text-center py-12 text-base-content/60">
            <Clock size={48} className="mx-auto mb-4 opacity-50" />
            <p>No past sessions found. Head to the dashboard to start one.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="table w-full">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>ID</th>
                  <th>Mode</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {sessions.map((s) => (
                  <tr key={s.id} className="hover">
                    <td>
                      <div className="font-semibold">{new Date(s.date).toLocaleDateString()}</div>
                      <div className="text-xs opacity-60">{new Date(s.date).toLocaleTimeString()}</div>
                    </td>
                    <td className="font-mono text-xs opacity-70">{s.id.split('-')[0]}...</td>
                    <td>
                      <span className="capitalize font-medium">{s.mode}</span>
                    </td>
                    <td>{getStatusBadge(s.status)}</td>
                    <td>
                      <button 
                        className="btn btn-sm btn-ghost text-primary"
                        onClick={() => onViewSession(s.id)}
                        disabled={s.status !== 'completed'}
                      >
                        <Eye size={16} /> View
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
