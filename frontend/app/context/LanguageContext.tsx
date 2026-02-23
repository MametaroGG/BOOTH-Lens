"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { translations, Language, Translation } from "../lib/translations";

interface LanguageContextType {
    language: Language;
    t: Translation;
    setLanguage: (lang: Language) => void;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export function LanguageProvider({ children }: { children: ReactNode }) {
    const [language, setLanguage] = useState<Language>("ja"); // Default to Japanese as requested

    const value = {
        language,
        t: translations[language],
        setLanguage,
    };

    return (
        <LanguageContext.Provider value={value}>
            {children}
        </LanguageContext.Provider>
    );
}

export function useLanguage() {
    const context = useContext(LanguageContext);
    if (context === undefined) {
        throw new Error("useLanguage must be used within a LanguageProvider");
    }
    return context;
}
