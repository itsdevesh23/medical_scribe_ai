import { useState } from 'react';
import Dashboard from './components/Dashboard';
import SessionViewer from './components/SessionViewer';
import History from './components/History';
import { Activity, LayoutDashboard, History as HistoryIcon } from 'lucide-react';

function App() {
  const [currentView, setCurrentView] = useState('dashboard'); // 'dashboard', 'history', 'viewer'
  const [activeSessionId, setActiveSessionId] = useState(null);

  const viewSession = (sessionId) => {
    setActiveSessionId(sessionId);
    setCurrentView('viewer');
  };

  return (
    <div className="min-h-screen flex flex-col bg-base-200">
      {/* Navbar */}
      <div className="navbar bg-base-100 shadow-sm px-8 border-b border-base-300">
        <div className="flex-1">
          <a className="btn btn-ghost normal-case text-xl font-bold flex items-center gap-2" onClick={() => setCurrentView('dashboard')}>
            <div className="p-2 bg-primary text-primary-content rounded-lg">
              <Activity size={20} />
            </div>
            MedMeet Scribe
          </a>
        </div>
        <div className="flex-none gap-2">
          <button 
            className={`btn btn-sm ${currentView === 'dashboard' ? 'btn-primary' : 'btn-ghost'}`}
            onClick={() => setCurrentView('dashboard')}
          >
            <LayoutDashboard size={16} /> Dashboard
          </button>
          <button 
            className={`btn btn-sm ${currentView === 'history' ? 'btn-primary' : 'btn-ghost'}`}
            onClick={() => setCurrentView('history')}
          >
            <HistoryIcon size={16} /> History
          </button>
        </div>
      </div>

      {/* Main Content */}
      <main className="flex-1 p-8 max-w-7xl mx-auto w-full">
        {currentView === 'dashboard' && <Dashboard onViewSession={viewSession} />}
        {currentView === 'history' && <History onViewSession={viewSession} />}
        {currentView === 'viewer' && activeSessionId && (
          <SessionViewer sessionId={activeSessionId} onBack={() => setCurrentView('history')} />
        )}
      </main>
    </div>
  );
}

export default App;
