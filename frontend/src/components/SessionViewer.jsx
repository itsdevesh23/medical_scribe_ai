import { useState, useEffect } from 'react';
import axios from 'axios';
import { ArrowLeft, Download, FileText, MessageSquare, Loader2 } from 'lucide-react';

const BASE_URL = `${window.location.protocol}//${window.location.hostname}:8000`;

export default function SessionViewer({ sessionId, onBack }) {
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSession = async () => {
      try {
        const res = await axios.get(`${BASE_URL}/api/sessions/${sessionId}`);
        setSession(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchSession();
  }, [sessionId]);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-[50vh]">
        <Loader2 className="animate-spin text-primary" size={48} />
      </div>
    );
  }

  if (!session) {
    return <div className="text-center text-error">Session not found.</div>;
  }

  const { report, transcript, mode } = session;

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex justify-between items-center bg-base-100 p-4 rounded-xl shadow-sm border border-base-200">
        <button className="btn btn-ghost" onClick={onBack}>
          <ArrowLeft size={20} /> Back to History
        </button>
        <h2 className="text-2xl font-bold">Session Details</h2>
        <a 
          href={`${BASE_URL}/api/sessions/${sessionId}/report.pdf`}
          download
          className="btn btn-primary"
        >
          <Download size={20} /> Download PDF
        </a>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Report Card */}
        <div className="card bg-base-100 shadow-xl border border-base-200">
          <div className="card-body">
            <h3 className="card-title flex items-center gap-2 text-primary border-b border-base-200 pb-4">
              <FileText />
              {mode === 'medical' ? 'SOAP Note' : 'Meeting Minutes'}
            </h3>
            <div className="prose prose-sm max-w-none mt-4 overflow-y-auto max-h-[60vh] pr-2">
              <pre className="bg-base-200 p-4 rounded-lg whitespace-pre-wrap overflow-x-auto text-sm">
                {JSON.stringify(report, null, 2)}
              </pre>
            </div>
          </div>
        </div>

        {/* Transcript Card */}
        <div className="card bg-base-100 shadow-xl border border-base-200">
          <div className="card-body">
            <h3 className="card-title flex items-center gap-2 text-secondary border-b border-base-200 pb-4">
              <MessageSquare />
              Transcript
            </h3>
            <div className="mt-4 space-y-4 overflow-y-auto max-h-[60vh] pr-2">
              {transcript?.map((seg, idx) => (
                <div key={idx} className={`chat ${seg.speaker === 'Doctor' || seg.speaker.includes('1') ? 'chat-end' : 'chat-start'}`}>
                  <div className="chat-header font-semibold opacity-70 mb-1">
                    {seg.speaker}
                  </div>
                  <div className={`chat-bubble ${seg.speaker === 'Doctor' || seg.speaker.includes('1') ? 'chat-bubble-primary' : 'chat-bubble-secondary'}`}>
                    {seg.text}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
