import React, { useState } from 'react';
import axios from 'axios';
import { Music, AlertTriangle, Download, RefreshCw, CheckCircle2, Info, X } from 'lucide-react';
import DropZone from './components/DropZone';
import StarBackground from './components/StarBackground';
import './App.css';

function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [convertedUrl, setConvertedUrl] = useState(null);
  const [downloadName, setDownloadName] = useState("");
  const [highFi, setHighFi] = useState(true);
  const [showInfo, setShowInfo] = useState(false);

  const handleFileSelected = (selectedFile) => {
    setError(null);
    convertFile(selectedFile);
  };

  const convertFile = async (currentFile) => {
    setIsLoading(true);
    setConvertedUrl(null);

    const formData = new FormData();
    formData.append('file', currentFile);

    try {
      const response = await axios.post(`/convert?high_fidelity=${highFi}`, formData, {
        responseType: 'blob', // Important for binary download
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      setConvertedUrl(url);
      setDownloadName(currentFile.name.replace(/\.[^/.]+$/, "") + ".mid");

    } catch (err) {
      console.error(err);
      let errorMessage = "Conversion failed. Please check the file and try again.";

      if (err.response && err.response.data instanceof Blob) {
        try {
          const text = await err.response.data.text();
          const json = JSON.parse(text);
          console.error("Backend Error Trace:", json.trace);
          if (json.message) {
            errorMessage = `Server Error: ${json.message}`;
          }
        } catch (e) {
          console.error("Failed to parse error blob:", e);
        }
      }
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const reset = () => {
    setConvertedUrl(null);
    setError(null);
  };

  return (
    <div className="container">
      <StarBackground />
      <header className="header">
        <img src="/logo.svg" alt="GP2MIDI Logo" className="logo" />
        <h1>GP2MIDI Pro</h1>
        <p>Studio-Grade Guitar Pro to MIDI Converter</p>
      </header>

      <div className="controls">
        <label className="switch-container">
          <input
            type="checkbox"
            checked={highFi}
            onChange={(e) => setHighFi(e.target.checked)}
            disabled={isLoading}
          />
          <span className="switch-label">
            High Fidelity Mode
            <button
              className="info-btn"
              onClick={(e) => { e.preventDefault(); setShowInfo(true); }}
              title="What is High Fidelity Mode?"
            >
              <Info size={16} />
            </button>
          </span>
        </label>
      </div>

      <main className="main-content">
        {error && (
          <div className="error-banner">
            <AlertTriangle size={20} />
            {error}
            <button onClick={() => setError(null)} className="close-btn">&times;</button>
          </div>
        )}

        {!convertedUrl ? (
          <div className="upload-section">
            <DropZone onFileSelected={handleFileSelected} isLoading={isLoading} />
            {isLoading && (
              <div className="loading-indicator">
                <RefreshCw className="spin" size={32} />
                <p>Processing...</p>
              </div>
            )}
          </div>
        ) : (
          <div className="success-card">
            <div className="success-icon">
              <CheckCircle2 size={64} color="var(--accent-primary)" />
            </div>
            <h2>Conversion Complete!</h2>
            <p>{downloadName}</p>

            <div className="actions">
              <a href={convertedUrl} download={downloadName} className="btn-primary">
                <Download size={20} /> Download MIDI
              </a>
              <button onClick={reset} className="btn-secondary">
                Convert Another
              </button>
            </div>
          </div>
        )}
      </main>

      <footer className="footer">
        <Music size={16} /> Powered by GP2MIDI Engine
      </footer>

      {showInfo && (
        <div className="modal-overlay" onClick={() => setShowInfo(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3>High Fidelity Mode (MPE Style)</h3>
              <button className="close-modal-btn" onClick={() => setShowInfo(false)}>
                <X size={20} />
              </button>
            </div>
            <div className="modal-body">
              <div className="feature-block">
                <h4><CheckCircle2 size={16} className="icon-on" /> What stays ON</h4>
                <p>
                  Allocates a <strong>separate MIDI channel</strong> for each guitar string (Channels 1-6).
                  This allows for <strong>independent pitch bends</strong> per note.
                </p>
                <p className="highlight">
                  Essential for songs where you bend one string while letting another ring (e.g., Unison Bends).
                </p>
              </div>

              <div className="feature-block warning">
                <h4><AlertTriangle size={16} className="icon-warn" /> Considerations</h4>
                <ul>
                  <li>Uses <strong>6 channels</strong> per guitar track.</li>
                  <li>Can clutter basic MIDI editors.</li>
                  <li>Requires a synth/sampler that supports multi-channel input (Omnisphere, Kontakt, etc.).</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
