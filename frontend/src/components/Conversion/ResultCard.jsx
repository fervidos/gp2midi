import React from 'react';
import { CheckCircle2, Download, RefreshCw } from 'lucide-react';

const ResultCard = ({ downloadName, convertedUrl, onReset }) => {
    return (
        <div className="success-card">
            <div className="success-icon">
                <CheckCircle2 size={64} color="var(--accent-primary)" />
                <div className="success-glow"></div>
            </div>
            <h2>Conversion Complete!</h2>
            <p className="filename">{downloadName}</p>

            <div className="actions">
                <a href={convertedUrl} download={downloadName} className="btn-primary">
                    <Download size={20} /> <span>Download MIDI</span>
                    <div className="btn-glow"></div>
                </a>
                <button onClick={onReset} className="btn-secondary">
                    <RefreshCw size={16} /> Convert Another
                </button>
            </div>
        </div>
    );
};

export default ResultCard;
