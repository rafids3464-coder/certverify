/**
 * ResultCard.js - Displays the comprehensive prediction result.
 * Shows: prediction badge, confidence bar, score breakdowns.
 */

import React from "react";

function ScoreBar({ label, value, color }) {
    const pct = Math.round(value * 100);
    return (
        <div style={{ marginBottom: 12 }}>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
                <span style={{ fontSize: "0.8rem", color: "var(--text-secondary)", fontWeight: 500 }}>
                    {label}
                </span>
                <span
                    style={{
                        fontSize: "0.8rem",
                        fontWeight: 700,
                        fontFamily: "'JetBrains Mono', monospace",
                        color,
                    }}
                >
                    {pct}%
                </span>
            </div>
            <div className="progress-bar-track">
                <div
                    className="progress-bar-fill"
                    style={{ width: `${pct}%`, background: color }}
                />
            </div>
        </div>
    );
}

export default function ResultCard({ result }) {
    const isReal = result.prediction === "REAL";
    const confidencePct = result.confidence.toFixed(1);

    const mainColor = isReal ? "var(--accent-green)" : "var(--accent-red)";
    const mainGrad = isReal ? "var(--grad-real)" : "var(--grad-fake)";

    return (
        <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>

            {/* ── Header: Verdict ─────────────────────────────────────────────── */}
            <div
                style={{
                    padding: "28px 32px",
                    borderRadius: "var(--radius-lg)",
                    background: isReal
                        ? "rgba(16, 185, 129, 0.08)"
                        : "rgba(239, 68, 68, 0.08)",
                    border: `1px solid ${isReal ? "rgba(16,185,129,0.25)" : "rgba(239,68,68,0.25)"}`,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    flexWrap: "wrap",
                    gap: 16,
                }}
            >
                <div>
                    <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 8 }}>
                        Judgment
                    </div>
                    <div
                        style={{
                            fontSize: "2.5rem",
                            fontWeight: 900,
                            background: mainGrad,
                            WebkitBackgroundClip: "text",
                            WebkitTextFillColor: "transparent",
                            backgroundClip: "text",
                            letterSpacing: "-0.02em",
                        }}
                    >
                        {isReal ? "✓ AUTHENTIC" : "✗ FORGED"}
                    </div>
                    <div style={{ color: "var(--text-secondary)", marginTop: 4, fontSize: "0.9rem" }}>
                        Certificate appears to be <strong style={{ color: mainColor }}>{result.prediction}</strong>
                    </div>
                </div>

                {/* Confidence dial */}
                <div style={{ textAlign: "center" }}>
                    <div
                        style={{
                            width: 100,
                            height: 100,
                            borderRadius: "50%",
                            background: `conic-gradient(${mainColor} ${result.confidence * 3.6}deg, var(--bg-elevated) 0)`,
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            position: "relative",
                        }}
                    >
                        <div
                            style={{
                                width: 80,
                                height: 80,
                                borderRadius: "50%",
                                background: "var(--bg-base)",
                                display: "flex",
                                flexDirection: "column",
                                alignItems: "center",
                                justifyContent: "center",
                            }}
                        >
                            <span style={{ fontSize: "1.4rem", fontWeight: 800, fontFamily: "'JetBrains Mono', monospace", color: mainColor }}>
                                {confidencePct}
                            </span>
                            <span style={{ fontSize: "0.65rem", color: "var(--text-muted)" }}>%</span>
                        </div>
                    </div>
                    <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: 8 }}>Confidence</div>
                </div>
            </div>

            {/* ── Score Breakdown ──────────────────────────────────────────────── */}
            <div className="card" style={{ padding: "24px 28px" }}>
                <h3 style={{ marginBottom: 20, fontSize: "1rem", color: "var(--text-secondary)", textTransform: "uppercase", letterSpacing: "0.08em" }}>
                    Score Breakdown
                </h3>
                <ScoreBar
                    label="🧠 CNN (EfficientNet-B0)"
                    value={result.cnn_score}
                    color="#7c3aed"
                />
                <ScoreBar
                    label="🔍 CLIP Semantic Match"
                    value={result.clip_score}
                    color="#00d4ff"
                />
                <ScoreBar
                    label="🛡️ Tamper Integrity"
                    value={result.tamper_score}
                    color="#10b981"
                />

                {/* Weight legend */}
                <div
                    style={{
                        marginTop: 20,
                        padding: "12px 16px",
                        background: "var(--bg-elevated)",
                        borderRadius: "var(--radius-sm)",
                        fontSize: "0.75rem",
                        color: "var(--text-muted)",
                        fontFamily: "'JetBrains Mono', monospace",
                    }}
                >
                    Final = 0.6×CNN + 0.2×CLIP + 0.2×Tamper
                </div>
            </div>

        </div>
    );
}
