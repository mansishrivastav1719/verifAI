import "./Hero.css";

const Hero = () => {
    return (
        <section className="w-full hero bg-blue-400">
            <div className="hero-left">
                <h1>Detect Document<br />Forgery with AI</h1>
                <p className="text-white">
                    Upload any document (PDF/Image) and get instant
                    forensic analysis with explainable signals.
                </p>

                <div className="badges">
                    <span>⚡ Under 20s</span>
                    <span>💻 CPU-only</span>
                    <span>🔍 3+ signals</span>
                    <span>📍 Localization</span>
                </div>
            </div>

            <div className="hero-right">
                <div className="upload-box">
                    <div className="icon">☁️</div>
                    <p>Drag & Drop or Click to Upload</p>
                    <small>PDF, PNG, JPG (Max 16MB)</small>
                    <button>Choose Document</button>
                </div>
            </div>
        </section>
    );
};

export default Hero;
