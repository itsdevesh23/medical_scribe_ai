import { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Upload, Mic, Stethoscope, Users, CheckCircle, Loader2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const BASE_URL = `${window.location.protocol}//${window.location.hostname}:8000`;
const WS_URL = `ws://${window.location.hostname}:8000/ws`;

export default function Dashboard({ onViewSession }) {
  const [mode, setMode] = useState('medical');
  const [inputType, setInputType] = useState('upload'); // 'upload' or 'record'
  const [file, setFile] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  
  const fileInputRef = useRef(null);
  const wsRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const timerIntervalRef = useRef(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        const audioFile = new File([audioBlob], 'live_recording.webm', { type: 'audio/webm' });
        setFile(audioFile);
        
        // Stop all tracks to release the mic
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
      setRecordingTime(0);
      setFile(null); // Clear any previously selected file
      
      timerIntervalRef.current = setInterval(() => {
        setRecordingTime((prevTime) => prevTime + 1);
      }, 1000);

    } catch (error) {
      console.error('Error accessing microphone:', error);
      alert('Could not access microphone. Please check permissions.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      clearInterval(timerIntervalRef.current);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (wsRef.current) wsRef.current.close();
      if (timerIntervalRef.current) clearInterval(timerIntervalRef.current);
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
        mediaRecorderRef.current.stop();
        if (mediaRecorderRef.current.stream) {
          mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
        }
      }
    };
  }, []);

  const handleUpload = async () => {
    if (!file) return;
    setIsProcessing(true);
    setProgress('uploading');

    const formData = new FormData();
    formData.append('file', file);
    formData.append('mode', mode);

    try {
      const response = await axios.post(`${BASE_URL}/api/sessions`, formData);
      const newSessionId = response.data.session_id;
      setSessionId(newSessionId);
      setProgress('pending');
      connectWebSocket(newSessionId);
    } catch (error) {
      console.error(error);
      setIsProcessing(false);
      setProgress(null);
      alert('Upload failed');
    }
  };

  const connectWebSocket = (sid) => {
    const ws = new WebSocket(`${WS_URL}/${sid}`);
    wsRef.current = ws;

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setProgress(data.status);
      if (data.status === 'completed' || data.status === 'failed') {
        ws.close();
        if (data.status === 'completed') {
          setTimeout(() => onViewSession(sid), 1500);
        } else {
          setIsProcessing(false);
          alert('Processing failed');
        }
      }
    };
  };

  const steps = ['pending', 'transcribing', 'diarizing', 'aligning', 'generating_report', 'generating_pdf', 'completed'];
  const getStepIndex = (status) => steps.indexOf(status);
  const currentIndex = getStepIndex(progress);

  return (
    <div className="flex flex-col items-center justify-center min-h-[70vh]">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="card w-full max-w-3xl bg-base-100 shadow-xl border border-base-200"
      >
        <div className="card-body p-10">
          <h2 className="text-3xl font-extrabold text-center mb-2">New Session</h2>
          <p className="text-center text-base-content/70 mb-8">Upload audio or record live to generate structured notes offline.</p>

          {!isProcessing ? (
            <AnimatePresence>
              <motion.div 
                initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                className="space-y-8"
              >
                {/* Mode Selection */}
                <div className="grid grid-cols-2 gap-4">
                  <button
                    className={`btn h-32 flex flex-col gap-3 ${mode === 'medical' ? 'btn-primary shadow-lg ring-2 ring-primary ring-offset-2 ring-offset-base-100' : 'btn-outline border-base-300'}`}
                    onClick={() => setMode('medical')}
                  >
                    <Stethoscope size={32} />
                    <span className="text-lg">Doctor-Patient</span>
                  </button>
                  <button
                    className={`btn h-32 flex flex-col gap-3 ${mode === 'meeting' ? 'btn-primary shadow-lg ring-2 ring-primary ring-offset-2 ring-offset-base-100' : 'btn-outline border-base-300'}`}
                    onClick={() => setMode('meeting')}
                  >
                    <Users size={32} />
                    <span className="text-lg">Meeting Minutes</span>
                  </button>
                </div>

                {/* Input Type Selection */}
                <div role="tablist" className="tabs tabs-boxed bg-base-200 p-1">
                  <a role="tab" className={`tab ${inputType === 'upload' ? 'tab-active bg-base-100 shadow' : ''}`} onClick={() => setInputType('upload')}>Upload File</a>
                  <a role="tab" className={`tab ${inputType === 'record' ? 'tab-active bg-base-100 shadow' : ''}`} onClick={() => setInputType('record')}>Record Live</a>
                </div>

                {/* Input Area */}
                {inputType === 'upload' ? (
                  <div 
                    className="border-2 border-dashed border-base-300 rounded-2xl p-12 text-center hover:bg-base-200/50 transition-colors cursor-pointer group"
                    onClick={() => fileInputRef.current?.click()}
                  >
                    <input
                      type="file"
                      ref={fileInputRef}
                      onChange={handleFileChange}
                      accept="audio/wav,audio/mp3,audio/webm"
                      className="hidden"
                    />
                    <div className="flex flex-col items-center gap-4 text-base-content/60 group-hover:text-primary transition-colors">
                      <Upload size={48} />
                      {file ? (
                        <span className="text-xl font-semibold text-primary">{file.name}</span>
                      ) : (
                        <div>
                          <span className="text-lg font-medium block">Click to select audio file</span>
                          <span className="text-sm">or drag and drop here</span>
                        </div>
                      )}
                    </div>
                  </div>
                ) : (
                  <div className="border-2 border-base-300 rounded-2xl p-12 text-center bg-base-200/30">
                    <div className="flex flex-col items-center gap-6">
                      <div className="text-4xl font-mono tracking-wider font-bold text-base-content/80">
                        {formatTime(recordingTime)}
                      </div>
                      
                      {!isRecording ? (
                        <button 
                          className="btn btn-error btn-circle btn-lg text-error-content shadow-lg animate-pulse"
                          onClick={startRecording}
                        >
                          <Mic size={32} />
                        </button>
                      ) : (
                        <button 
                          className="btn btn-neutral btn-circle btn-lg shadow-lg"
                          onClick={stopRecording}
                        >
                          <div className="w-6 h-6 bg-current rounded-sm"></div>
                        </button>
                      )}
                      
                      {file && !isRecording && (
                        <div className="text-success font-medium flex items-center gap-2 mt-4">
                          <CheckCircle size={20} /> Recording saved successfully
                        </div>
                      )}
                      {!file && !isRecording && (
                        <div className="text-base-content/60 mt-4">
                          Click the microphone to start recording
                        </div>
                      )}
                    </div>
                  </div>
                )}

                <div className="flex justify-end pt-4">
                  <button 
                    className="btn btn-primary btn-lg w-full sm:w-auto px-12 rounded-full"
                    disabled={!file || isRecording}
                    onClick={handleUpload}
                  >
                    Start Processing
                  </button>
                </div>
              </motion.div>
            </AnimatePresence>
          ) : (
            <motion.div 
              initial={{ opacity: 0, scale: 0.95 }} 
              animate={{ opacity: 1, scale: 1 }}
              className="py-12 px-4"
            >
              <h3 className="text-2xl font-bold text-center mb-12">Processing Audio...</h3>
              <ul className="steps steps-vertical lg:steps-horizontal w-full">
                {steps.map((step, idx) => (
                  <li 
                    key={step} 
                    className={`step ${idx <= currentIndex ? 'step-primary' : ''} ${idx === currentIndex && step !== 'completed' ? 'animate-pulse' : ''}`}
                  >
                    {step.replace('_', ' ').toUpperCase()}
                  </li>
                ))}
              </ul>
              {progress !== 'completed' && (
                <div className="flex justify-center mt-12">
                  <span className="loading loading-spinner loading-lg text-primary"></span>
                </div>
              )}
            </motion.div>
          )}
        </div>
      </motion.div>
    </div>
  );
}
