/**
 * pages/result.js - Certificate analysis result display page.
 *
 * Shows: prediction verdict, confidence dial, score breakdowns,
 * ELA tampering heatmap, and OCR extracted text.
 */

import React, { useEffect, useState } from "react";
import Link from "next/link";
import Head from "next/head";
import { useRouter } from "next/router";
import ResultCard from "../components/ResultCard";
import HeatmapDisplay from "../components/HeatmapDisplay";

export default function ResultPage() {
    const router = useRouter();
    const [result, setResult] = useState(null);
    const [loaded, setLoaded] = useState(false);

    useEffect(() => {
        const raw = sessionStorage.getItem("certResult");
        if (!raw) {
            router.replace("/upload");
            return;
        }
        try {
            setResult(JSON.parse(raw));
        } catch {
            router.replace("/upload");
            return;
        }
        setLoaded(true);
    }, [router]);

    if (!loaded || !result) {
        return (
            <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center" }}>
                <div className="spinner" />
            </div>
        );
    }

    const isReal = result.prediction === "REAL";
    const ocr = result.ocr || {};

    return (
        <>
            <Head>
                <title>{result.prediction} — {result.filename} — CertVerify</title>
                <meta name="description" content={`Certificate analysis result: ${result.prediction} with ${result.confidence.toFixed(1)}% confidence.`} />
            </Head>

            <div className="page-wrapper">
                {/* Navbar */}
                <nav className="navbar">
                    <div className="navbar-inner">
                        <Link href="/" className="navbar-logo">
                            <div className="logo-icon">🔏</div>
                            <span>CertVerify</span>
                        </Link>
                        <ul className="navbar-links">
                            <li><Link href="/">Home</Link></li>
                            <li><Link href="/upload">Upload</Link></li>
                        </ul>
                        <Link href="/upload" className="btn btn-secondary" style={{ padding: "8px 18px", fontSize: "0.875rem" }}>
                            + New Analysis
                        </Link>
                    </div>
                </nav>

                <main className="container" style={{ padding: "48px 24px 80px", maxWidth: 1100 }}>

                    {/* Header */}
                    <div style={{ marginBottom: 40 }}>
                        <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 8 }}>
                            <span className={`badge ${isReal ? "badge-real" : "badge-fake"}`} style={{ fontSize: "0.9rem", padding: "8px 18px" }}>
                                {isReal ? "✓ AUTHENTIC" : "✗ FORGED"}
                            </span>
                            <span className="badge badge-info">
                                {result.confidence.toFixed(1)}% Confidence
                            </span>
                        </div>
                        <h1 style={{ marginBottom: 8, fontSize: "clamp(1.5rem, 3vw, 2rem)" }}>
                            Analysis Report
                        </h1>
                        <p style={{ fontSize: "0.875rem", color: "var(--text-muted)" }}>
                            File: <code style={{ color: "var(--accent-cyan)", background: "var(--bg-elevated)", padding: "2px 8px", borderRadius: 4 }}>{result.filename}</code>
                            {result.timestamp && (
                                <> · {new Date(result.timestamp).toLocaleString()}</>
                            )}
                        </p>
                    </div>

                    {/* Main grid */}
                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24 }}>

                        {/* Left: Verdict + scores */}
                        <div style={{ gridColumn: "1 / 2" }}>
                            <ResultCard result={result} />
                        </div>

                        {/* Right: ELA Heatmap */}
                        <div
                            style={{ gridColumn: "2 / 3" }}
                            className="card"
                        >
                            <h3 style={{ marginBottom: 16, color: "var(--text-secondary)", fontSize: "0.85rem", textTransform: "uppercase", letterSpacing: "0.08em" }}>
                                🛡️ Tampering Heatmap (ELA)
                            </h3>
                            <HeatmapDisplay base64={result.heatmap_b64} filename={result.filename} />
                            <p style={{ marginTop: 12, fontSize: "0.78rem", color: "var(--text-muted)" }}>
                                Bright regions indicate potential tampering or copy-paste artifacts.
                                Warm colours = higher error level.
                            </p>
                        </div>

                        {/* OCR Results — full width */}
                        <div
                            style={{ gridColumn: "1 / -1" }}
                            className="card"
                        >
                            <h3 style={{ marginBottom: 20, color: "var(--text-secondary)", fontSize: "0.85rem", textTransform: "uppercase", letterSpacing: "0.08em" }}>
                                📝 OCR Extracted Text
                            </h3>

                            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 12, marginBottom: 20 }}>
                                {[
                                    { label: "University", value: ocr.university || "Not detected" },
                                    { label: "Date", value: ocr.date || "Not detected" },
                                    { label: "Roll No.", value: ocr.roll_number || "Not detected" },
                                ].map((f) => (
                                    <div key={f.label} className="ocr-field">
                                        <div className="ocr-label">{f.label}</div>
                                        <div className="ocr-value">{f.value}</div>
                                    </div>
                                ))}
                            </div>

                            {/* Text validity indicator */}
                            <div
                                style={{
                                    display: "flex",
                                    alignItems: "center",
                                    gap: 10,
                                    padding: "12px 16px",
                                    background: ocr.is_valid_text ? "rgba(16,185,129,0.08)" : "rgba(245,158,11,0.08)",
                                    border: `1px solid ${ocr.is_valid_text ? "rgba(16,185,129,0.25)" : "rgba(245,158,11,0.25)"}`,
                                    borderRadius: "var(--radius-sm)",
                                    fontSize: "0.8rem",
                                }}
                            >
                                <span style={{ fontSize: "1.1rem" }}>{ocr.is_valid_text ? "✅" : "⚠️"}</span>
                                <span style={{ color: ocr.is_valid_text ? "var(--accent-green)" : "var(--accent-amber)" }}>
                                    Text structure {ocr.is_valid_text ? "passed all validation checks" : "has anomalies"}
                                </span>
                                {ocr.anomaly_flags && ocr.anomaly_flags.length > 0 && (
                                    <span style={{ marginLeft: 8, color: "var(--text-muted)" }}>
                                        ({ocr.anomaly_flags.join(", ")})
                                    </span>
                                )}
                            </div>

                            {/* Raw OCR text collapsible */}
                            <details style={{ marginTop: 16 }}>
                                <summary style={{ cursor: "pointer", color: "var(--text-muted)", fontSize: "0.8rem", userSelect: "none" }}>
                                    View raw OCR text
                                </summary>
                                <pre
                                    style={{
                                        marginTop: 12,
                                        padding: 16,
                                        background: "var(--bg-elevated)",
                                        borderRadius: "var(--radius-sm)",
                                        fontSize: "0.75rem",
                                        color: "var(--text-secondary)",
                                        whiteSpace: "pre-wrap",
                                        wordBreak: "break-word",
                                        maxHeight: 200,
                                        overflowY: "auto",
                                        fontFamily: "'JetBrains Mono', monospace",
                                    }}
                                >
                                    {ocr.raw_text || "(no text extracted)"}
                                </pre>
                            </details>
                        </div>
                    </div>

                    {/* Actions */}
                    <div style={{ display: "flex", gap: 16, justifyContent: "center", marginTop: 40, flexWrap: "wrap" }}>
                        <Link href="/upload" className="btn btn-primary">
                            🔍 Analyse Another Certificate
                        </Link>
                        <button
                            className="btn btn-secondary"
                            onClick={() => window.print()}
                        >
                            🖨️ Print Report
                        </button>
                    </div>

                </main>
            </div>
        </>
    );
}
