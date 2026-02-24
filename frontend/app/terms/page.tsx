"use client";

import { useLanguage } from "../context/LanguageContext";
import LanguageSwitcher from "../components/LanguageSwitcher";
import { Search, ChevronLeft } from "lucide-react";
import Link from "next/link";

export default function TermsPage() {
    const { t } = useLanguage();

    return (
        <main className="flex min-h-screen flex-col items-center relative overflow-hidden bg-background selection:bg-blue-500/30">
            {/* Dynamic Background Elements */}
            <div className="absolute inset-0 bg-grid-white/5 bg-[size:40px_40px] pointer-events-none" />
            <div className="absolute inset-0 bg-gradient-to-b from-transparent via-background/50 to-background pointer-events-none" />
            <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-blue-600/5 rounded-full blur-[120px] pointer-events-none" />

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

            {/* Content Section */}
            <section className="w-full max-w-3xl mt-12 mb-24 px-8 z-10">
                <Link href="/" className="inline-flex items-center gap-2 text-zinc-500 hover:text-white transition-colors mb-12 text-sm font-bold group">
                    <ChevronLeft size={16} className="group-hover:-translate-x-1 transition-transform" />
                    {t.common.backToHome}
                </Link>

                <div className="glass-panel p-8 md:p-12 rounded-[2rem] border-white/5">
                    <h1 className="text-4xl font-black tracking-tighter text-white mb-4 uppercase italic">
                        {t.terms.title}
                    </h1>
                    <p className="text-sm font-bold text-zinc-500 tracking-widest mb-12 uppercase">{t.terms.updated}</p>

                    <div className="space-y-12">
                        <p className="text-lg text-zinc-300 leading-relaxed font-medium">
                            {t.terms.introduction}
                        </p>

                        {t.terms.sections.map((section, idx) => (
                            <div key={idx} className="space-y-4">
                                <h2 className="text-xl font-bold text-white tracking-tight pt-4 border-t border-white/5">
                                    {section.title}
                                </h2>
                                <p className="text-zinc-400 leading-relaxed font-medium whitespace-pre-line">
                                    {section.content}
                                </p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            <footer className="w-full py-12 px-8 border-t border-white/5 bg-zinc-950/50 z-10 backdrop-blur-3xl mt-auto">
                <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-8">
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
