import "./Requirements.css"

const Requirements = () => {
    return (
        <section className="requirements">
            <h2>Hackathon Requirements Met</h2>

            <div className="req-boxes">
                <div className="req-card">
                    <h3>Mandatory Constraints</h3>
                    <ul>
                        <li>✔ 3+ explainable signals</li>
                        <li>✔ Tamper localization</li>
                        <li>✔ OCR integration</li>
                        <li>✔ Uncertainty handling</li>
                    </ul>
                </div>

                <div className="req-card">
                    <h3>Performance Constraints</h3>
                    <ul>
                        <li>✔ Latency ≤ 20 seconds</li>
                        <li>✔ CPU-only operation</li>
                        <li>✔ PDF / PNG / JPG support</li>
                        <li>✔ No paid APIs</li>
                    </ul>
                </div>
            </div>
        </section>
    );
};

export default Requirements;
