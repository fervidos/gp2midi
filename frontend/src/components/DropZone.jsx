import React, { useCallback, useState } from 'react';
import { UploadCloud, FileMusic, AlertCircle } from 'lucide-react';
import './DropZone.css';

export default function DropZone({ onFileSelected, isLoading }) {
    const [isDragOver, setIsDragOver] = useState(false);
    const [error, setError] = useState(null);

    const handleDragOver = (e) => {
        e.preventDefault();
        setIsDragOver(true);
    };

    const handleDragLeave = (e) => {
        e.preventDefault();
        setIsDragOver(false);
    };

    const validateFile = (file) => {
        const ext = file.name.split('.').pop().toLowerCase();
        if (['gp3', 'gp4', 'gp5', 'gpx', 'gp'].includes(ext)) {
            setError(null);
            return true;
        }
        setError("Supported formats: .gp3, .gp4, .gp5, .gpx, .gp");
        return false;
    };

    const handleDrop = (e) => {
        e.preventDefault();
        setIsDragOver(false);

        if (isLoading) return;

        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            const file = e.dataTransfer.files[0];
            if (validateFile(file)) {
                onFileSelected(file);
            }
        }
    };

    const handleChange = (e) => {
        if (e.target.files && e.target.files.length > 0) {
            const file = e.target.files[0];
            if (validateFile(file)) {
                onFileSelected(file);
            }
        }
    };

    return (
        <div
            className={`drop-zone ${isDragOver ? 'drag-over' : ''} ${isLoading ? 'disabled' : ''}`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => document.getElementById('fileInput').click()}
        >
            <input
                type="file"
                id="fileInput"
                style={{ display: 'none' }}
                accept=".gp3,.gp4,.gp5,.gpx,.gp"
                onChange={handleChange}
                disabled={isLoading}
            />

            <div className="icon-wrapper">
                <UploadCloud size={48} color={isDragOver ? "var(--accent-primary)" : "var(--text-muted)"} />
            </div>

            <h3>
                {isDragOver ? "Drop it here!" : "Drag & Drop Guitar Pro File"}
            </h3>
            <p className="subtext">Supported: GP3, GP4, GP5, GPX, GP</p>

            {error && (
                <div className="error-badge">
                    <AlertCircle size={16} /> {error}
                </div>
            )}
        </div>
    );
}
