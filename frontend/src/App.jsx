import React, { useState } from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

import Header from './components/Header';
import DropZone from './components/Conversion/DropZone';
import ConversionControls from './components/Conversion/ConversionControls';
import TrackSelector from './components/Conversion/TrackSelector';
import ResultCard from './components/Conversion/ResultCard';
import InfoModal from './components/Modals/InfoModal';
import StarBackground from './components/StarBackground';
import { useConversion } from './hooks/useConversion';

import './App.css';

function App() {
  const {
    isLoading, error, convertedUrl, downloadName,
    highFi, setHighFi, analyzeFile, convertFile, reset, setError, analysisData, setAnalysisData
  } = useConversion();

  const [showInfo, setShowInfo] = useState(false);

  return (
    <div className="container">
      <StarBackground />

      <Header />

      <div className="main-layout">
        {!convertedUrl && !analysisData && (
          <ConversionControls
            highFi={highFi}
            setHighFi={setHighFi}
            onOpenInfo={() => setShowInfo(true)}
            disabled={isLoading}
          />
        )}

        <main className="main-content">
          {error && (
            <div className="error-banner">
              <AlertTriangle size={20} />
              <span>{error}</span>
              <button onClick={() => setError(null)} className="close-btn">&times;</button>
            </div>
          )}

          {!convertedUrl ? (
            <div className="upload-section">
              {!analysisData ? (
                <>
                  <DropZone onFileSelected={analyzeFile} isLoading={isLoading} />
                  {isLoading && (
                    <div className="loading-indicator">
                      <RefreshCw className="spin" size={32} />
                      <p>Processing...</p>
                    </div>
                  )}
                </>
              ) : (
                <TrackSelector
                  tracks={analysisData.tracks}
                  onConfirm={convertFile}
                  onCancel={() => setAnalysisData(null)}
                  isLoading={isLoading}
                />
              )}
            </div>
          ) : (
            <ResultCard
              downloadName={downloadName}
              convertedUrl={convertedUrl}
              onReset={reset}
            />
          )}
        </main>
      </div>

      <footer className="footer">
        Powered by GP2MIDI Engine V2
      </footer>

      {showInfo && <InfoModal onClose={() => setShowInfo(false)} />}
    </div>
  );
}

export default App;
