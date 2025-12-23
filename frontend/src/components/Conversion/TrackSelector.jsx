import React, { useState, useEffect } from 'react';
import { Music, Check, X, Disc } from 'lucide-react';
import './TrackSelector.css';

const TrackSelector = ({ tracks, onConfirm, onCancel, isLoading }) => {
    const [selectedIds, setSelectedIds] = useState([]);

    // Initialize with all tracks selected
    useEffect(() => {
        if (tracks && tracks.length > 0) {
            setSelectedIds(tracks.map(t => t.id));
        }
    }, [tracks]);

    const toggleTrack = (id) => {
        setSelectedIds(prev => {
            if (prev.includes(id)) {
                return prev.filter(tid => tid !== id);
            } else {
                return [...prev, id];
            }
        });
    };

    const handleSelectAll = () => {
        setSelectedIds(tracks.map(t => t.id));
    };

    const handleDeselectAll = () => {
        setSelectedIds([]);
    };

    return (
        <div className="track-selector-card">
            <div className="track-selector-header">
                <h3><Music size={20} /> Select Instruments</h3>
                <p>Choose which tracks to include in the MIDI file</p>
            </div>

            <div className="track-list-actions">
                <button onClick={handleSelectAll} className="text-btn">All</button>
                <span className="separator">|</span>
                <button onClick={handleDeselectAll} className="text-btn">None</button>
                <span className="track-count">{selectedIds.length} selected</span>
            </div>

            <div className="track-list">
                {tracks.map(track => (
                    <div
                        key={track.id}
                        className={`track-item ${selectedIds.includes(track.id) ? 'selected' : ''}`}
                        onClick={() => toggleTrack(track.id)}
                    >
                        <div className="track-checkbox">
                            {selectedIds.includes(track.id) ? <Check size={14} /> : null}
                        </div>
                        <div className="track-info">
                            <span className="track-name">{track.name}</span>
                            <span className="track-details">
                                CH {track.channel + 1} • {track.is_percussion ? 'Drums' : `Prog ${track.program}`}
                            </span>
                        </div>
                        {track.is_percussion && <Disc size={16} className="drum-icon" />}
                    </div>
                ))}
            </div>

            <div className="track-selector-footer">
                <button className="cancel-btn" onClick={onCancel} disabled={isLoading}>
                    Cancel
                </button>
                <button
                    className="confirm-btn"
                    onClick={() => onConfirm(selectedIds)}
                    disabled={isLoading || selectedIds.length === 0}
                >
                    {isLoading ? 'Converting...' : 'Convert Selected'}
                </button>
            </div>
        </div>
    );
};

export default TrackSelector;
