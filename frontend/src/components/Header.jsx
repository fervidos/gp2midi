import React from 'react';

const Header = () => {
    return (
        <header className="header">
            <div className="logo-container">
                <img src="/logo.svg" alt="GP2MIDI Logo" className="logo" />
                <div className="logo-glow"></div>
            </div>
            <h1>GP2MIDI <span className="pro-badge">PRO</span></h1>
            <p>Studio-Grade Guitar Pro to MIDI Converter</p>
        </header>
    );
};

export default Header;
