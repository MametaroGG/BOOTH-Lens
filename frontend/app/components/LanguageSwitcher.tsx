"use client";

import { useLanguage } from "../context/LanguageContext";
import { Globe } from "lucide-react";

export default function LanguageSwitcher() {
    const { language, setLanguage } = useLanguage();

    return (
        <button
            onClick={() => setLanguage(language === "en" ? "ja" : "en")}
            className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-gray-800 hover:bg-gray-700 text-gray-300 text-sm transition-colors border border-gray-700"
        >
            <Globe size={16} />
            <span>{language === "en" ? "English" : "日本語"}</span>
        </button>
    );
}
