/**
 * pages/index.js — Home/Landing page (v2).
 * Uses shared Navbar (with 3-dot menu). Upload stays as hero CTA only.
 */

import React from "react";
import Link from "next/link";
import Head from "next/head";
import Navbar from "../components/Navbar";

const FEATURES = [
    { icon: "🧠", title: "Deep Learning CNN", desc: "EfficientNet-B0 fully fine-tuned on 15k+ real & forged certificate images.", bg: "rgba(124,58,237,0.12)" },
    { icon: "🔍", title: "CLIP Semantic Analysis", desc: "OpenAI CLIP validates image-text coherence to catch semantic forgeries.", bg: "rgba(0,212,255,0.1)" },
    { icon: "🛡️", title: "Error Level Analysis", desc: "JPEG re-compression forensics reveals copy-paste tampering as a heatmap.", bg: "rgba(16,185,129,0.1)" },
    { icon: "📝", title: "OCR Validation", desc: "Tesseract OCR extracts key fields and flags text anomalies.", bg: "rgba(245,158,11,0.1)" },
];

const STATS = [
    { value: "95%+", label: "Detection Accuracy" },
    { value: "< 5s", label: "Analysis Time" },
    { value: "3", label: "AI Models" },
    { value: "PDF/JPG/PNG", label: "Formats" },
];

export default function HomePage() {
    return (
        <>
            <Head>
                <title>CertVerify — Fake Certificate Detection</title>
                <meta name="description" content="AI-powered fake certificate detection using CNN, CLIP, OCR, and ELA." />
                <link rel="icon" href="/favicon.ico" />
            </Head>

            <div className="page-wrapper">
                <Navbar />

                <main>
                    {/* Hero */}
                    <div className="hero container">
                        <div className="hero-tag"><span>✨</span><span>Multi-Modal AI — CNN + CLIP + ELA + OCR</span></div>

                        <h1 className="hero-title">
                            Detect <span className="gradient-text">Forged Certificates</span>
                            <br />in Seconds
                        </h1>

                        <p className="hero-subtitle">
                            Upload any certificate — PDF, JPG, or PNG — and our AI pipeline instantly
                            determines authenticity using deep learning, semantic analysis, and tampering detection.
                        </p>

                        <div style={{ display: "flex", gap: 16, justifyContent: "center", flexWrap: "wrap" }}>
                            <Link href="/upload" className="btn btn-primary" style={{ padding: "14px 36px", fontSize: "1rem" }}>
                                🔍 Analyse a Certificate
                            </Link>
                            <Link href="/about" className="btn btn-secondary" style={{ padding: "14px 28px", fontSize: "1rem" }}>
                                📖 How It Works
                            </Link>
                        </div>
                    </div>

                    {/* Stats bar */}
                    <div style={{ background: "var(--bg-surface)", borderTop: "1px solid var(--border-subtle)", borderBottom: "1px solid var(--border-subtle)", padding: "32px 0" }}>
                        <div className="container">
                            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(140px,1fr))", gap: 24, textAlign: "center" }}>
                                {STATS.map((s) => (
                                    <div key={s.label}>
                                        <div style={{ fontSize: "2rem", fontWeight: 800, color: "var(--accent-cyan)", fontFamily: "'JetBrains Mono',monospace" }}>{s.value}</div>
                                        <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: 4, textTransform: "uppercase", letterSpacing: "0.06em" }}>{s.label}</div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>

                    {/* Features */}
                    <div className="container">
                        <div style={{ textAlign: "center", padding: "60px 0 20px" }}>
                            <h2>How It <span className="gradient-text">Works</span></h2>
                            <p style={{ marginTop: 12, maxWidth: 500, margin: "12px auto 0" }}>
                                Four complementary AI systems work in tandem to produce a reliable verdict.
                            </p>
                        </div>

                        <div className="features-grid">
                            {FEATURES.map((f) => (
                                <div key={f.title} className="feature-card">
                                    <div className="feature-icon" style={{ background: f.bg }}>{f.icon}</div>
                                    <h3 style={{ marginBottom: 10 }}>{f.title}</h3>
                                    <p style={{ fontSize: "0.875rem" }}>{f.desc}</p>
                                </div>
                            ))}
                        </div>

                        {/* CTA */}
                        <div style={{
                            margin: "40px 0 80px", padding: "40px", borderRadius: "var(--radius-xl)",
                            background: "linear-gradient(135deg,rgba(124,58,237,0.15) 0%,rgba(0,212,255,0.08) 100%)",
                            border: "1px solid var(--border-accent)", textAlign: "center"
                        }}>
                            <h2 style={{ marginBottom: 16 }}>Ready to verify a certificate?</h2>
                            <p style={{ marginBottom: 28 }}>Get a detailed analysis report in under 5 seconds.</p>
                            <Link href="/upload" className="btn btn-primary" style={{ padding: "14px 40px" }}>
                                Get Started — It&apos;s Free
                            </Link>
                        </div>
                    </div>
                </main>

                <footer style={{ borderTop: "1px solid var(--border-subtle)", padding: "24px", textAlign: "center", color: "var(--text-muted)", fontSize: "0.85rem" }}>
                    CertVerify © 2026 — AI-Powered Certificate Authentication
                </footer>
            </div>
        </>
    );
}
