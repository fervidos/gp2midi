import React, { useState } from 'react';
import axios from 'axios';
import { Music, AlertTriangle, Download, RefreshCw, CheckCircle2 } from 'lucide-react';
import DropZone from './components/DropZone';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [convertedUrl, setConvertedUrl] = useState(null);
  const [downloadName, setDownloadName] = useState("");
  const [highFi, setHighFi] = useState(true);

  const handleFileSelected = (selectedFile) => {
    setFile(selectedFile);
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
      setError("Conversion failed. Please check the file and try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const reset = () => {
    setFile(null);
    setConvertedUrl(null);
    setError(null);
  };

  return (
    <div className="container">
      <header className="header">
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
            <span className="tooltip">Uses split channels for accurate bends (MPE style)</span>
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
    </div>
  );
}

export default App;
