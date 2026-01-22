import "./main.css";
    const Footer = () => {
    return (
        <>
            {/* OUR TEAM */}
            <section className="team">
                <h2>Our Team</h2>

                <div className="team-cards">
                    <div className="team-card">
                        <h3>💻</h3>
                        <h4>Pankaj</h4>
                        <p>Backend & System Architecture</p>
                    </div>

                    <div className="team-card">
                        <h3>🎨</h3>
                        <h4>Priyanka</h4>
                        <p>Frontend & Visualization</p>
                    </div>

                    <div className="team-card">
                        <h3>🧠</h3>
                        <h4>Mansi</h4>
                        <p>AI Algorithms & Signal Processing</p>
                    </div>

                    <div className="team-card">
                        <h3>📄</h3>
                        <h4>Arif</h4>
                        <p>Documentation & Presentation</p>
                    </div>
                </div>
            </section>

            {/* FOOTER */}
            <footer className="footer">
                <p>
                    Built for <strong>HackTheWinter 2026</strong> •
                    ML-103: Explainable Document Forgery Detection
                </p>
                <span>
                    24-hour Hackathon Project • All mandatory requirements implemented
                </span>
            </footer>
        </>
    );
};

export default Footer;
