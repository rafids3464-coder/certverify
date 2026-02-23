/**
 * DropZone.js - Drag & drop file upload component.
 * Accepts PDF, JPG, PNG files. Shows visual feedback on drag-over.
 */

import React, { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";

const ACCEPTED_TYPES = {
    "image/jpeg": [".jpg", ".jpeg"],
    "image/png": [".png"],
    "application/pdf": [".pdf"],
};

const MAX_SIZE = 20 * 1024 * 1024; // 20 MB

export default function DropZone({ onFileAccepted, isLoading }) {
    const [error, setError] = useState("");

    const onDrop = useCallback(
        (acceptedFiles, rejectedFiles) => {
            setError("");
            if (rejectedFiles.length > 0) {
                const code = rejectedFiles[0].errors?.[0]?.code;
                if (code === "file-too-large")
                    setError("File is too large. Maximum size is 20 MB.");
                else if (code === "file-invalid-type")
                    setError("Invalid file type. Please upload JPG, PNG, or PDF.");
                else
                    setError("File rejected. Please try another file.");
                return;
            }
            if (acceptedFiles.length > 0) {
                onFileAccepted(acceptedFiles[0]);
            }
        },
        [onFileAccepted]
    );

    const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
        onDrop,
        accept: ACCEPTED_TYPES,
        maxSize: MAX_SIZE,
        multiple: false,
        disabled: isLoading,
    });

    return (
        <div style={{ width: "100%" }}>
            <div
                {...getRootProps()}
                className={`dropzone${isDragActive ? " active" : ""}${isDragReject ? " reject" : ""}`}
                style={{
                    borderColor: isDragReject
                        ? "var(--accent-red)"
                        : isDragActive
                            ? "var(--accent-cyan)"
                            : undefined,
                    opacity: isLoading ? 0.6 : 1,
                    cursor: isLoading ? "not-allowed" : "pointer",
                }}
            >
                <input {...getInputProps()} id="file-upload-input" />

                {/* Upload icon */}
                <div
                    className="animate-float"
                    style={{ fontSize: "4rem", marginBottom: "20px", lineHeight: 1 }}
                >
                    {isDragActive ? "📂" : "📄"}
                </div>

                {isDragActive ? (
                    <p style={{ fontSize: "1.2rem", fontWeight: 600, color: "var(--accent-cyan)" }}>
                        Drop your certificate here...
                    </p>
                ) : (
                    <>
                        <p style={{ fontSize: "1.15rem", fontWeight: 600, color: "var(--text-primary)", marginBottom: 12 }}>
                            Drag & drop your certificate
                        </p>
                        <p style={{ color: "var(--text-muted)", marginBottom: 24, fontSize: "0.9rem" }}>
                            or click to browse from your computer
                        </p>

                        <div style={{ display: "flex", gap: 10, justifyContent: "center", flexWrap: "wrap" }}>
                            {["JPG", "PNG", "PDF"].map((ext) => (
                                <span key={ext} className="badge badge-info" style={{ fontSize: "0.75rem" }}>
                                    {ext}
                                </span>
                            ))}
                        </div>

                        <p style={{ color: "var(--text-muted)", marginTop: 16, fontSize: "0.8rem" }}>
                            Maximum file size: 20 MB
                        </p>
                    </>
                )}
            </div>

            {error && (
                <div
                    style={{
                        marginTop: 12,
                        padding: "12px 16px",
                        background: "rgba(239, 68, 68, 0.1)",
                        border: "1px solid rgba(239, 68, 68, 0.3)",
                        borderRadius: "var(--radius-sm)",
                        color: "var(--accent-red)",
                        fontSize: "0.875rem",
                        display: "flex",
                        alignItems: "center",
                        gap: 8,
                    }}
                >
                    ⚠️ {error}
                </div>
            )}
        </div>
    );
}
