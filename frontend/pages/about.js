/**
 * pages/about.js — About page explaining the system architecture.
 */

import React from "react";
import Head from "next/head";
import Link from "next/link";
import Navbar from "../components/Navbar";

const TECH = [
    { icon: "🧠", name: "EfficientNet-B0", desc: "CNN backbone fine-tuned on 15k+ certificate images (real + 5 forgery types)", color: "#7c3aed" },
    { icon: "🔍", name: "CLIP (ViT-B/32)", desc: "OpenAI's vision-language model validates semantic coherence between image and text", color: "#00d4ff" },
    { icon: "🛡️", name: "Error Level Analysis", desc: "JPEG re-compression forensics reveals copy-paste manipulation regions", color: "#10b981" },
    { icon: "📝", name: "Tesseract OCR", desc: "Extracts university name, date, roll number and checks for text anomalies", color: "#f59e0b" },
];

export default function AboutPage() {
    return (
        <>
            <Head><title>About — CertVerify</title></Head>
            <div className="page-wrapper">
                <Navbar />
                <main className="container" style={{ padding: "60px 24px 80px", maxWidth: 900 }}>

                    <div style={{ textAlign: "center", marginBottom: 60 }}>
                        <h1 style={{ fontSize: "clamp(2rem,5vw,3rem)", marginBottom: 16 }}>
                            How <span className="gradient-text">CertVerify</span> Works
                        </h1>
                        <p style={{ maxWidth: 600, margin: "0 auto", fontSize: "1rem" }}>
                            A multi-modal AI system combining deep learning, semantic analysis, and digital forensics to detect forged certificates in seconds.
                        </p>
                    </div>

                    {/* Tech grid */}
                    <div className="features-grid" style={{ marginBottom: 60 }}>
                        {TECH.map((t) => (
                            <div key={t.name} className="feature-card">
                                <div className="feature-icon" style={{ background: `${t.color}20`, fontSize: "1.8rem" }}>{t.icon}</div>
                                <h3 style={{ marginBottom: 8, color: t.color }}>{t.name}</h3>
                                <p style={{ fontSize: "0.875rem" }}>{t.desc}</p>
                            </div>
                        ))}
                    </div>

                    {/* Formula card */}
                    <div className="card" style={{ textAlign: "center", padding: "36px 28px", marginBottom: 48 }}>
                        <h2 style={{ marginBottom: 12 }}>Final Scoring Formula</h2>
                        <div style={{
                            background: "var(--bg-elevated)", borderRadius: "var(--radius-sm)", padding: "18px 24px",
                            fontFamily: "'JetBrains Mono',monospace", fontSize: "1.1rem", color: "var(--accent-cyan)"
                        }}>
                            Score = 0.6 × CNN + 0.2 × CLIP + 0.2 × ELA
                        </div>
                        <p style={{ marginTop: 14, fontSize: "0.875rem" }}>
                            Certificates scoring above 50% are classified as <strong>REAL</strong>; below is <strong>FAKE</strong>.
                        </p>
                    </div>

                    {/* CTA */}
                    <div style={{ textAlign: "center" }}>
                        <Link href="/upload" className="btn btn-primary" style={{ padding: "14px 36px" }}>
                            Try It Now →
                        </Link>
                    </div>

                </main>
            </div>
        </>
    );
}
