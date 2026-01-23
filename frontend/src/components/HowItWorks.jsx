import react from "react"
import "./HowItWorks.css"

const HowItWorks = () => {
    return (
        <section className="how">
            <h2>How It Works</h2>

            <div className="how-cards">
                <div className="card">
                    <h3>🔴 Error Level Analysis</h3>
                    <p>
                        Detects copy-paste and editing artifacts by analyzing
                        JPEG compression levels across the document.
                    </p>
                </div>

                <div className="card">
                    <h3>🟡 Text Inconsistency</h3>
                    <p>
                        Identifies font, size, and alignment inconsistencies
                        using OCR and pattern recognition.
                    </p>
                </div>

                <div className="card">
                    <h3>🟢 Metadata Forensics</h3>
                    <p>
                        Analyzes document metadata for anomalies like
                        creation and modification date mismatches.
                    </p>
                </div>
            </div>
        </section>
    );
};

export default HowItWorks;
