import React from 'react';
import { X, CheckCircle2, AlertTriangle } from 'lucide-react';

const InfoModal = ({ onClose }) => {
    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content" onClick={e => e.stopPropagation()}>
                <div className="modal-header">
                    <h3>High Fidelity Mode (MPE Style)</h3>
                    <button className="close-modal-btn" onClick={onClose}>
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
    );
};

export default InfoModal;
