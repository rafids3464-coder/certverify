/**
 * HeatmapDisplay.js - Renders the base64-encoded ELA tampering heatmap.
 */

import React, { useState } from "react";

export default function HeatmapDisplay({ base64, filename = "certificate" }) {
    const [enlarged, setEnlarged] = useState(false);

    if (!base64) {
        return (
            <div
                style={{
                    width: "100%",
                    aspectRatio: "4/3",
                    background: "var(--bg-elevated)",
                    border: "1px dashed var(--border-subtle)",
                    borderRadius: "var(--radius-md)",
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    justifyContent: "center",
                    gap: 12,
                    color: "var(--text-muted)",
                }}
            >
                <span style={{ fontSize: "2.5rem" }}>🔍</span>
                <p style={{ fontSize: "0.875rem" }}>Heatmap not available</p>
            </div>
        );
    }

    const src = `data:image/png;base64,${base64}`;

    return (
        <>
            <div
                className="heatmap-container"
                onClick={() => setEnlarged(true)}
                style={{ cursor: "zoom-in", position: "relative" }}
            >
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={src} alt="ELA Tampering Heatmap" style={{ width: "100%", display: "block" }} />
                <div
                    style={{
                        position: "absolute",
                        bottom: 12,
                        right: 12,
                        background: "rgba(0,0,0,0.7)",
                        backdropFilter: "blur(8px)",
                        color: "white",
                        padding: "4px 10px",
                        borderRadius: 6,
                        fontSize: "0.75rem",
                        fontWeight: 500,
                    }}
                >
                    🔍 Click to enlarge
                </div>
            </div>

            {/* Lightbox */}
            {enlarged && (
                <div
                    onClick={() => setEnlarged(false)}
                    style={{
                        position: "fixed",
                        inset: 0,
                        background: "rgba(0,0,0,0.9)",
                        zIndex: 1000,
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        padding: 24,
                        cursor: "zoom-out",
                    }}
                >
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img
                        src={src}
                        alt="ELA Heatmap (enlarged)"
                        style={{ maxWidth: "95vw", maxHeight: "90vh", borderRadius: 12 }}
                        onClick={(e) => e.stopPropagation()}
                    />
                    <button
                        onClick={() => setEnlarged(false)}
                        style={{
                            position: "absolute",
                            top: 24,
                            right: 24,
                            background: "rgba(255,255,255,0.1)",
                            border: "none",
                            color: "white",
                            fontSize: "1.5rem",
                            width: 44,
                            height: 44,
                            borderRadius: "50%",
                            cursor: "pointer",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                        }}
                    >
                        ×
                    </button>
                </div>
            )}
        </>
    );
}
