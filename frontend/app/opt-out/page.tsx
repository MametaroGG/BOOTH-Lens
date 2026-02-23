"use client";

import { useState } from "react";
import axios from "axios";
import { useLanguage } from "../context/LanguageContext";
import LanguageSwitcher from "../components/LanguageSwitcher";
import { Search, ShieldCheck, Mail, AlertCircle, ChevronLeft } from "lucide-react";
import Link from "next/link";

export default function OptOutPage() {
    const [shopUrl, setShopUrl] = useState("");
    const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle");
    const { t } = useLanguage();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setStatus("loading");
        try {
            await axios.post("/api/opt-out", { shopUrl });
            setStatus("success");
            setShopUrl(""); // Clear input on success
        } catch (err) {
            console.error(err);
            setStatus("error");
        }
    };

    return (
        <main className="flex min-h-screen flex-col items-center relative overflow-hidden bg-background selection:bg-blue-500/30">
            {/* Dynamic Background Elements */}
            <div className="absolute inset-0 bg-grid-white/5 bg-[size:40px_40px] pointer-events-none" />
            <div className="absolute inset-0 bg-gradient-to-b from-transparent via-background/50 to-background pointer-events-none" />

            {/* Navigation */}
            <header className="w-full max-w-7xl flex justify-between items-center px-8 py-8 z-50">
                <Link href="/" className="flex items-center gap-3 group cursor-pointer">
                    <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-2xl transition-transform group-hover:scale-110">
                        <Search className="text-white w-5 h-5" strokeWidth={3} />
                    </div>
                    <span className="text-xl font-black tracking-tighter text-white uppercase italic">
                        {t.common.appName}
                    </span>
                </Link>
                <LanguageSwitcher />
            </header>

            <div className="w-full max-w-xl px-8 z-10 mt-12 mb-24">
                <div className="glass-panel p-8 md:p-12 rounded-[2.5rem] border-white/5 shadow-2xl">
                    <div className="w-16 h-16 rounded-[1.5rem] bg-zinc-900 border border-white/5 flex items-center justify-center text-blue-500 mb-8 mx-auto shadow-2xl">
                        <ShieldCheck size={32} />
                    </div>

                    <h1 className="text-4xl font-black tracking-tighter text-white mb-6 text-center uppercase italic">
                        {t.optOut.title}
                    </h1>
                    <p className="text-zinc-500 text-center font-medium leading-relaxed mb-12">
                        {t.optOut.description}
                    </p>

                    <form onSubmit={handleSubmit} className="space-y-8">
                        <div className="space-y-3">
                            <label className="text-[10px] font-black text-zinc-500 uppercase tracking-[0.2em] ml-2">
                                {t.optOut.label}
                            </label>
                            <div className="relative group">
                                <div className="absolute inset-y-0 left-5 flex items-center pointer-events-none text-zinc-500 group-focus-within:text-blue-500 transition-colors">
                                    <Search size={18} />
                                </div>
                                <input
                                    type="url"
                                    required
                                    placeholder={t.optOut.placeholder}
                                    value={shopUrl}
                                    onChange={(e) => setShopUrl(e.target.value)}
                                    className="w-full pl-14 pr-6 py-5 bg-black/40 border border-white/5 rounded-2xl text-white font-bold placeholder:text-zinc-700 focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all"
                                />
                            </div>
                        </div>

                        <button
                            type="submit"
                            disabled={status === "loading" || status === "success"}
                            className="w-full bg-blue-600 hover:bg-blue-500 disabled:bg-zinc-800 disabled:text-zinc-500 text-white font-black tracking-widest uppercase py-5 rounded-2xl transition-all shadow-xl shadow-blue-500/20 active:scale-95 flex items-center justify-center gap-3"
                        >
                            <Mail size={18} strokeWidth={3} />
                            {status === "loading" ? t.common.submitting : status === "success" ? t.common.submitted : t.common.submit}
                        </button>

                        {status === "success" && (
                            <div className="p-5 bg-green-500/10 text-green-400 text-sm font-bold rounded-2xl border border-green-500/20 flex items-center gap-4 animate-in fade-in slide-in-from-top-4">
                                <ShieldCheck size={24} />
                                {t.optOut.success}
                            </div>
                        )}

                        {status === "error" && (
                            <div className="p-5 bg-red-500/10 text-red-400 text-sm font-bold rounded-2xl border border-red-500/20 flex items-center gap-4 animate-in shake">
                                <AlertCircle size={24} />
                                {t.optOut.failed}
                            </div>
                        )}
                    </form>

                    <div className="mt-12 text-center">
                        <Link href="/" className="text-xs font-black text-zinc-600 hover:text-white uppercase tracking-widest transition-colors flex items-center justify-center gap-2">
                            <ChevronLeft size={16} strokeWidth={3} />
                            {t.common.backToHome}
                        </Link>
                    </div>
                </div>
            </div>

            {/* Footer */}
            <footer className="w-full py-12 px-8 border-t border-white/5 bg-zinc-950/50 z-10 backdrop-blur-3xl mt-auto">
                <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-8 text-[10px] font-bold text-zinc-600 tracking-[0.3em] uppercase">
                    &copy; 2026 豆々庵. BOOTH-LENS. ALL RIGHTS RESERVED.
                    <div className="flex gap-6">
                        <Link href="/privacy" className="text-zinc-500 hover:text-white transition-colors">{t.home.footer.privacy}</Link>
                        <Link href="/terms" className="text-zinc-500 hover:text-white transition-colors">{t.home.footer.terms}</Link>
                    </div>
                </div>
            </footer>
        </main>
    );
}
