import { useState } from 'react';
import axios from 'axios';

export const useConversion = () => {
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [convertedUrl, setConvertedUrl] = useState(null);
    const [downloadName, setDownloadName] = useState("");
    const [highFi, setHighFi] = useState(true);

    const [analysisData, setAnalysisData] = useState(null);
    const [currentFile, setCurrentFile] = useState(null);

    const analyzeFile = async (file) => {
        setIsLoading(true);
        setError(null);
        setAnalysisData(null);
        setCurrentFile(file);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await axios.post('/api/analyze', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            setAnalysisData(response.data);
        } catch (err) {
            console.error(err);
            setError("Analysis failed. Please check the file and try again.");
        } finally {
            setIsLoading(false);
        }
    };

    const convertFile = async (selectedTracks = []) => {
        if (!currentFile) return;

        setIsLoading(true);
        setConvertedUrl(null);
        setError(null);

        const formData = new FormData();
        formData.append('file', currentFile);

        let url = `/api/convert?high_fidelity=${highFi}`;
        if (selectedTracks.length > 0) {
            url += `&selected_tracks=${selectedTracks.join(',')}`;
        }

        try {
            const response = await axios.post(url, formData, {
                responseType: 'blob',
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });

            const resultUrl = window.URL.createObjectURL(new Blob([response.data]));
            setConvertedUrl(resultUrl);
            setDownloadName(currentFile.name.replace(/\.[^/.]+$/, "") + ".mid");

            // Clear analysis data after successful conversion
            setAnalysisData(null);

        } catch (err) {
            console.error(err);
            let errorMessage = "Conversion failed. Please try again.";

            if (err.response && err.response.data instanceof Blob) {
                try {
                    const text = await err.response.data.text();
                    const json = JSON.parse(text);
                    if (json.detail && json.detail.message) {
                        errorMessage = `Server Error: ${json.detail.message}`;
                    } else if (json.detail) {
                        errorMessage = json.detail;
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
        setDownloadName("");
        setAnalysisData(null);
        setCurrentFile(null);
    };

    return {
        isLoading,
        error,
        convertedUrl,
        downloadName,
        highFi,
        analysisData,
        setHighFi,
        analyzeFile,
        convertFile,
        reset,
        setError,
        setAnalysisData
    };
};
