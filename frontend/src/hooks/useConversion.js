import { useState } from 'react';
import axios from 'axios';

export const useConversion = () => {
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [convertedUrl, setConvertedUrl] = useState(null);
    const [downloadName, setDownloadName] = useState("");
    const [highFi, setHighFi] = useState(true);

    const convertFile = async (currentFile) => {
        setIsLoading(true);
        setConvertedUrl(null);
        setError(null);

        const formData = new FormData();
        formData.append('file', currentFile);

        try {
            // Use config from Vite proxy or relative path
            const response = await axios.post(`/api/convert?high_fidelity=${highFi}`, formData, {
                responseType: 'blob',
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });

            const url = window.URL.createObjectURL(new Blob([response.data]));
            setConvertedUrl(url);
            setDownloadName(currentFile.name.replace(/\.[^/.]+$/, "") + ".mid");

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
                        errorMessage = json.detail; // Flattened detail string
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
    };

    return {
        isLoading,
        error,
        convertedUrl,
        downloadName,
        highFi,
        setHighFi,
        convertFile,
        reset,
        setError
    };
};
