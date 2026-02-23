/**
 * pages/upload.js - Certificate upload page with drag & drop.
 * Shows analysis progress and redirects to result page on success.
 */

import React, { useState, useRef } from "react";
import { useRouter } from "next/router";
import Link from "next/link";
import Head from "next/head";
import axios from "axios";
import DropZone from "../components/DropZone";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const ANALYSIS_STEPS = [
    { icon: "🖼️", label: "Processing image..." },
    { icon: "🧠", label: "Running CNN analysis..." },
    { icon: "📝", label: "Extracting OCR text..." },
    { icon: "🔍", label: "Running CLIP semantic check..." },
    { icon: "🛡️", label: "Computing ELA tampering score..." },
    { icon: "⚖️", label: "Calculating final verdict..." },
];

export default function UploadPage() {
    const router = useRouter();
    const [file, setFile] = useState(null);
    const [isAnalysing, setIsAnalysing] = useState(false);
    const [error, setError] = useState("");
    const [stepIdx, setStepIdx] = useState(0);
    const stepTimer = useRef(null);

    const handleFileAccepted = (f) => {
        setFile(f);
        setError("");
    };

    const simulateSteps = () => {
        let idx = 0;
        setStepIdx(0);
        stepTimer.current = setInterval(() => {
            idx++;
            if (idx < ANALYSIS_STEPS.length) setStepIdx(idx);
            else clearInterval(stepTimer.current);
        }, 800);
    };

    const handleAnalyse = async () => {
        if (!file) { setError("Please select a file first."); return; }
        setIsAnalysing(true);
        setError("");
        simulateSteps();

        const formData = new FormData();
        formData.append("file", file);

        try {
            const res = await axios.post(`${API_URL}/api/upload`, formData, {
                headers: { "Content-Type": "multipart/form-data" },
                timeout: 120000, // 2-min timeout for first inference
            });

            clearInterval(stepTimer.current);

            // Store result in sessionStorage and navigate to result page
            sessionStorage.setItem("certResult", JSON.stringify(res.data));
            router.push("/result");

        } catch (err) {
            clearInterval(stepTimer.current);
            setIsAnalysing(false);
            const msg =
                err.response?.data?.detail ||
                err.message ||
                "Analysis failed. Please try again.";
            setError(msg);
        }
    };

    return (
        <>
            <Head>
                <title>Upload Certificate — CertVerify</title>
                <meta name="description" content="Upload your certificate for AI-powered authenticity verification." />
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
                    </div>
                </nav>

                <main className="container" style={{ padding: "60px 24px", maxWidth: 720 }}>

                    <div style={{ textAlign: "center", marginBottom: 48 }}>
                        <div className="hero-tag" style={{ display: "inline-flex" }}>
                            <span>Step 1 of 2</span> — Upload Certificate
                        </div>
                        <h1 style={{ marginTop: 16, fontSize: "clamp(1.8rem, 4vw, 2.5rem)" }}>
                            Upload Your <span className="gradient-text">Certificate</span>
                        </h1>
                        <p style={{ marginTop: 12 }}>
                            Accepts JPG, PNG, and PDF (first page analysed). Max 20 MB.
                        </p>
                    </div>

                    {/* Dropzone */}
                    {!isAnalysing && (
                        <DropZone onFileAccepted={handleFileAccepted} isLoading={isAnalysing} />
                    )}

                    {/* Selected file preview */}
                    {file && !isAnalysing && (
                        <div
                            style={{
                                marginTop: 20,
                                padding: "16px 20px",
                                background: "var(--bg-elevated)",
                                border: "1px solid var(--border-subtle)",
                                borderRadius: "var(--radius-md)",
                                display: "flex",
                                alignItems: "center",
                                gap: 16,
                            }}
                        >
                            <div style={{ fontSize: "2.5rem" }}>
                                {file.name.endsWith(".pdf") ? "📄" : "🖼️"}
                            </div>
                            <div style={{ flex: 1, minWidth: 0 }}>
                                <div style={{ fontWeight: 600, color: "var(--text-primary)", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                                    {file.name}
                                </div>
                                <div style={{ fontSize: "0.8rem", color: "var(--text-muted)", marginTop: 2 }}>
                                    {(file.size / 1024).toFixed(1)} KB · {file.type || "document"}
                                </div>
                            </div>
                            <button
                                onClick={() => setFile(null)}
                                style={{ background: "none", border: "none", color: "var(--text-muted)", cursor: "pointer", fontSize: "1.2rem", padding: 4 }}
                                title="Remove file"
                            >
                                ×
                            </button>
                        </div>
                    )}

                    {/* Error message */}
                    {error && (
                        <div
                            style={{
                                marginTop: 16,
                                padding: "14px 18px",
                                background: "rgba(239,68,68,0.1)",
                                border: "1px solid rgba(239,68,68,0.3)",
                                borderRadius: "var(--radius-sm)",
                                color: "var(--accent-red)",
                                fontSize: "0.875rem",
                            }}
                        >
                            ⚠️ {error}
                        </div>
                    )}

                    {/* Analysis progress */}
                    {isAnalysing && (
                        <div className="card" style={{ textAlign: "center", padding: "48px 32px" }}>
                            <div className="spinner" style={{ margin: "0 auto 24px" }} />
                            <h3 style={{ marginBottom: 8 }}>Analysing Certificate…</h3>
                            <p style={{ marginBottom: 32, fontSize: "0.9rem" }}>
                                This may take up to 30 seconds on first run.
                            </p>
                            <div style={{ display: "flex", flexDirection: "column", gap: 10, maxWidth: 360, margin: "0 auto" }}>
                                {ANALYSIS_STEPS.map((step, i) => (
                                    <div
                                        key={step.label}
                                        style={{
                                            display: "flex",
                                            alignItems: "center",
                                            gap: 10,
                                            opacity: i <= stepIdx ? 1 : 0.3,
                                            transition: "opacity 0.4s",
                                            fontSize: "0.875rem",
                                        }}
                                    >
                                        <span>{i < stepIdx ? "✅" : i === stepIdx ? step.icon : "⏳"}</span>
                                        <span style={{ color: i <= stepIdx ? "var(--text-primary)" : "var(--text-muted)" }}>
                                            {step.label}
                                        </span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Analyse button */}
                    {!isAnalysing && (
                        <button
                            id="analyse-btn"
                            onClick={handleAnalyse}
                            disabled={!file}
                            className="btn btn-primary"
                            style={{ width: "100%", marginTop: 24, padding: "16px", fontSize: "1rem" }}
                        >
                            🔍 Analyse Certificate
                        </button>
                    )}

                </main>
            </div>
        </>
    );
}
