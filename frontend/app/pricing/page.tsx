"use client";

import { Check, Search, ChevronLeft } from "lucide-react";
import axios from "axios";
import { useState } from "react";
import { useLanguage } from "../context/LanguageContext";
import LanguageSwitcher from "../components/LanguageSwitcher";
import Link from "next/link";

export default function PricingPage() {
    const [loading, setLoading] = useState(false);
    const { t } = useLanguage();

    const handleSubscribe = async () => {
        setLoading(true);
        try {
            const userId = "demo-user-id";
            const email = "demo@example.com";

            const response = await axios.post("/api/subscription/checkout", {
                user_id: userId,
                email: email
            });

            if (response.data.url) {
                window.location.href = response.data.url;
            }
        } catch (err) {
            console.error(err);
            alert("Failed to start checkout. Please try again.");
            setLoading(false);
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

            {/* Hero Section */}
            <section className="w-full max-w-5xl mt-12 mb-16 text-center px-6 z-10">
                <h1 className="text-5xl md:text-7xl font-black tracking-tighter text-white mb-6 uppercase italic">
                    {t.pricing.title}
                </h1>
                <p className="text-lg md:text-xl text-zinc-500 max-w-2xl mx-auto leading-relaxed font-medium">
                    {t.pricing.subtitle}
                </p>
            </section>

            <div className="grid md:grid-cols-2 gap-8 w-full max-w-4xl px-8 z-10 mb-24">
                {/* Free Plan */}
                <div className="glass-panel p-8 md:p-10 rounded-[2.5rem] flex flex-col border-white/5">
                    <div className="mb-8">
                        <h2 className="text-[10px] font-black tracking-[0.3em] text-zinc-500 uppercase mb-2">{t.pricing.free}</h2>
                        <div className="text-5xl font-black text-white tracking-tighter tabular-nums">
                            {t.pricing.freePrice}<span className="text-sm font-bold text-zinc-600 ml-1 tracking-normal">{t.pricing.perMonth}</span>
                        </div>
                    </div>
                    <ul className="space-y-4 mb-12 flex-1">
                        <li className="flex items-center gap-3 text-sm font-bold text-zinc-300">
                            <Check size={18} strokeWidth={3} className="text-blue-500" />
                            <span>{t.pricing.features.free.searchLimit}</span>
                        </li>
                        <li className="flex items-center gap-3 text-sm font-bold text-zinc-300">
                            <Check size={18} strokeWidth={3} className="text-blue-500" />
                            <span>{t.pricing.features.free.basicResults}</span>
                        </li>
                        <li className="flex items-center gap-3 text-sm font-bold text-zinc-600 opacity-50">
                            <Check size={18} strokeWidth={3} />
                            <span className="line-through">{t.pricing.features.free.deepLogic}</span>
                        </li>
                    </ul>
                    <div className="w-full py-4 rounded-2xl bg-white/5 border border-white/5 text-zinc-400 text-sm font-black tracking-widest uppercase text-center cursor-default">
                        {t.pricing.currentPlan}
                    </div>
                </div>

                {/* Premium Plan */}
                <div className="glass-panel p-8 md:p-10 rounded-[2.5rem] flex flex-col relative overflow-hidden ring-2 ring-blue-500/50 bg-blue-600/5">
                    <div className="absolute top-6 right-8 bg-blue-600 text-[10px] font-black tracking-widest px-3 py-1.5 rounded-full uppercase">{t.pricing.popular}</div>
                    <div className="mb-8">
                        <h2 className="text-[10px] font-black tracking-[0.3em] text-blue-400 uppercase mb-2">{t.pricing.premium}</h2>
                        <div className="text-5xl font-black text-white tracking-tighter tabular-nums">
                            {t.pricing.premiumPrice}<span className="text-sm font-bold text-zinc-600 ml-1 tracking-normal">{t.pricing.perMonth}</span>
                        </div>
                    </div>
                    <ul className="space-y-4 mb-12 flex-1">
                        <li className="flex items-center gap-3 text-sm font-bold text-zinc-100">
                            <Check size={18} strokeWidth={3} className="text-blue-400" />
                            <span>{t.pricing.features.premium.unlimited}</span>
                        </li>
                        <li className="flex items-center gap-3 text-sm font-bold text-zinc-100">
                            <Check size={18} strokeWidth={3} className="text-blue-400" />
                            <span>{t.pricing.features.premium.fullResults}</span>
                        </li>
                        <li className="flex items-center gap-3 text-sm font-bold text-zinc-100">
                            <Check size={18} strokeWidth={3} className="text-blue-400" />
                            <span>{t.pricing.features.premium.advancedFilters}</span>
                        </li>
                        <li className="flex items-center gap-3 text-sm font-bold text-zinc-100">
                            <Check size={18} strokeWidth={3} className="text-blue-400" />
                            <span>{t.pricing.features.premium.directLinks}</span>
                        </li>
                    </ul>
                    <button
                        onClick={handleSubscribe}
                        disabled={loading}
                        className="w-full py-4 rounded-2xl bg-blue-600 hover:bg-blue-500 text-white text-sm font-black tracking-widest uppercase transition-all shadow-xl shadow-blue-500/20 active:scale-95 disabled:opacity-50"
                    >
                        {loading ? t.pricing.processing : t.pricing.upgradeNow}
                    </button>
                </div>
            </div>

            {/* Footer */}
            <footer className="w-full py-12 px-8 border-t border-white/5 bg-zinc-950/50 z-10 backdrop-blur-3xl mt-auto">
                <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-8">
                    <div className="flex items-center gap-2">
                        <div className="w-6 h-6 rounded-lg bg-blue-500 flex items-center justify-center">
                            <Search className="text-white w-3 h-3" strokeWidth={4} />
                        </div>
                        <span className="text-sm font-black tracking-tighter text-white uppercase italic">{t.common.appName}</span>
                    </div>
                    <div className="text-[10px] font-bold text-zinc-600 tracking-[0.3em] uppercase">
                        &copy; 2026 豆々庵. BoothPic. ALL RIGHTS RESERVED.
                    </div>
                    <div className="flex gap-6">
                        <Link href="/privacy" className="text-xs font-bold text-zinc-500 hover:text-white transition-colors">{t.home.footer.privacy}</Link>
                        <Link href="/terms" className="text-xs font-bold text-zinc-500 hover:text-white transition-colors">{t.home.footer.terms}</Link>
                    </div>
                </div>
            </footer>
        </main>
    );
}
