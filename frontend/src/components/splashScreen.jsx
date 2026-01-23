    import React from 'react';
    import { FileText } from 'lucide-react';

    export const SplashScreen = () => {
    return (
        <div 
        className="fixed inset-0 z-50 flex items-center justify-center"
        style={{ backgroundColor: '#667eea' }}
        data-testid="splash-screen"
        >
        <div className="flex items-center gap-2">
            <h1 
            className="text-6xl md:text-7xl lg:text-8xl font-bold text-white tracking-tight"
            style={{ fontFamily: "'Inter', sans-serif" }}
            data-testid="splash-screen-logo-text"
            >
            verifAi
            </h1>
            <FileText 
            className="text-white w-12 h-12 md:w-16 md:h-16 lg:w-20 lg:h-20 mt-2" 
            strokeWidth={2}
            data-testid="splash-screen-doc-icon"
            />
        </div>
        </div>
    );
    };

    export default SplashScreen;