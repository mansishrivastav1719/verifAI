import { useState, useEffect, useRef } from 'react';
import Navbar from "./components/Navbar";
import Hero from "./components/hero.jsx";
import HowItWorks from "./components/HowItWorks";
import Requirements from "./components/Requirements";
import Footer from "./components/footer.jsx";
import { SplashScreen } from "./components/splashScreen.jsx";

function App() {
    const [showSplash, setShowSplash] = useState(true);
    const detectRef = useRef(null);
    const howitworksRef = useRef(null);
    const requirementsRef = useRef(null);
    const footerRef = useRef(null);

    useEffect(() => {
        const timer = setTimeout(() => {
            setShowSplash(false);
        }, 2000);

        return () => clearTimeout(timer);
    }, []);

    const scrollToSection = (section) => {
        let ref;
        switch(section) {
            case 'detect':
                ref = detectRef;
                break;
            case 'howitworks':
                ref = howitworksRef;
                break;
            case 'requirements':
                ref = requirementsRef;
                break;
            case 'footer':
                ref = footerRef;
                break;
            default:
                return;
        }
        
        ref.current?.scrollIntoView({ behavior: 'smooth' });
    };

    return (
        <>
            {showSplash && <SplashScreen />}
            <Navbar onNavClick={scrollToSection} />
            <div ref={detectRef}>
                <Hero />
            </div>
            <div ref={howitworksRef}>
                <HowItWorks />
            </div>
            <div ref={requirementsRef}>
                <Requirements />
            </div>
            <div ref={footerRef}>
                <Footer/>
            </div>
        </>
    );
}

export default App;
