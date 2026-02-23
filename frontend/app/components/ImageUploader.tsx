"use client";

import { useState, useCallback } from "react";
import { Upload, X, ImageIcon, Search as SearchIcon } from "lucide-react";
import { useLanguage } from "../context/LanguageContext";

function cn(...classes: (string | undefined | null | false)[]) {
    return classes.filter(Boolean).join(" ");
}

interface ImageUploaderProps {
    onImageSelect: (file: File) => void;
}

export default function ImageUploader({ onImageSelect }: ImageUploaderProps) {
    const [preview, setPreview] = useState<string | null>(null);
    const [isDragging, setIsDragging] = useState(false);
    const { t } = useLanguage();

    const handleFile = useCallback((file: File) => {
        if (!file.type.startsWith("image/")) return;
        const reader = new FileReader();
        reader.onload = (e) => setPreview(e.target?.result as string);
        reader.readAsDataURL(file);
        onImageSelect(file);
    }, [onImageSelect]);

    const onDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
        if (e.dataTransfer.files?.[0]) {
            handleFile(e.dataTransfer.files[0]);
        }
    }, [handleFile]);

    return (
        <div className="w-full max-w-2xl mx-auto">
            <div
                onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
                onDragLeave={() => setIsDragging(false)}
                onDrop={onDrop}
                className={cn(
                    "relative overflow-hidden rounded-3xl transition-all duration-700 ease-in-out cursor-pointer group shadow-2xl ring-1 ring-white/10",
                    isDragging ? "bg-blue-600/10 ring-2 ring-blue-500" : "bg-zinc-900/40 hover:bg-zinc-800/40",
                    preview ? "h-[400px]" : "h-72 border-2 border-dashed border-white/5 hover:border-white/20"
                )}
            >
                <input
                    type="file"
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                    accept="image/*"
                    onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
                />

                {preview ? (
                    <div className="relative w-full h-full p-4 flex flex-col">
                        <div className="relative flex-1 rounded-2xl overflow-hidden glass-panel border-0 shadow-inner">
                            <img src={preview} alt="Preview" className="w-full h-full object-contain" />
                            <div className="absolute inset-0 pointer-events-none bg-gradient-to-t from-black/20 to-transparent" />
                        </div>
                        <div className="absolute top-8 right-8 flex gap-2">
                            <button
                                onClick={(e) => {
                                    e.preventDefault();
                                    setPreview(null);
                                }}
                                className="p-3 bg-white/10 hover:bg-white/20 text-white rounded-2xl backdrop-blur-2xl transition-all hover:scale-110 active:scale-95 border border-white/10"
                            >
                                <X size={20} />
                            </button>
                        </div>
                    </div>
                ) : (
                    <div className="flex flex-col items-center justify-center h-full px-8 text-center">
                        <div className={cn(
                            "w-20 h-20 rounded-[2.5rem] bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center mb-8 transition-all duration-500 shadow-2xl shadow-blue-500/40",
                            isDragging ? "scale-110 shadow-blue-500/60" : "group-hover:scale-105 group-hover:-translate-y-2 group-hover:shadow-blue-500/50"
                        )}>
                            <SearchIcon size={36} strokeWidth={2.5} className="text-white" />
                        </div>
                        <div className="space-y-1">
                            <p className="text-2xl font-bold tracking-tight text-white group-hover:text-blue-400 transition-colors">
                                {t.home.uploadPlaceholder}
                            </p>
                            <div className="flex items-center justify-center gap-3 pt-2">
                                <span className="h-[1px] w-8 bg-white/10" />
                                <p className="text-[10px] text-zinc-500 tracking-[0.2em] uppercase font-black">
                                    {t.home.uploadSupport}
                                </p>
                                <span className="h-[1px] w-8 bg-white/10" />
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
