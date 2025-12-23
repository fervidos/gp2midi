import React from 'react';
import { Info } from 'lucide-react';

const ConversionControls = ({ highFi, setHighFi, onOpenInfo, disabled }) => {
    return (
        <div className="controls">
            <label className={`switch-container ${disabled ? 'disabled' : ''}`}>
                <input
                    type="checkbox"
                    checked={highFi}
                    onChange={(e) => setHighFi(e.target.checked)}
                    disabled={disabled}
                />
                <div className="switch-toggle"></div>
                <span className="switch-label">
                    High Fidelity Mode
                    <button
                        className="info-btn"
                        onClick={(e) => { e.preventDefault(); onOpenInfo(); }}
                        title="What is High Fidelity Mode?"
                    >
                        <Info size={16} />
                    </button>
                </span>
            </label>
        </div>
    );
};

export default ConversionControls;
