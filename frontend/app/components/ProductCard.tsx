import { ExternalLink, Tag } from "lucide-react";
import { useLanguage } from "../context/LanguageContext";

interface ProductCardProps {
    title: string;
    price: string | number;
    thumbnailUrl: string;
    shopName: string;
    boothUrl: string;
    score?: number;
}

export default function ProductCard({ title, price, thumbnailUrl, shopName, boothUrl, score }: ProductCardProps) {
    const { t } = useLanguage();

    const formatPrice = (p: string | number) => {
        if (typeof p === 'string') {
            // Remove existing ¥ and normalize spacing
            const priceValue = p.replace('¥', '').trim();
            return `¥ ${priceValue}`;
        }
        return `¥ ${p.toLocaleString()}`;
    };

    return (
        <div className="group relative glass-panel rounded-2xl overflow-hidden transition-all duration-500 hover:shadow-2xl hover:shadow-blue-500/10 hover:-translate-y-2 hover:border-white/20">
            <div className="aspect-square overflow-hidden bg-zinc-900/50 relative">
                <img
                    src={thumbnailUrl}
                    alt={title}
                    className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-zinc-950/80 via-transparent to-transparent opacity-80" />

                {score && (
                    <div className="absolute top-3 right-3 bg-zinc-950/90 backdrop-blur-md px-2.5 py-1 rounded-full text-[10px] font-black tracking-widest text-zinc-100 border border-white/10 shadow-2xl uppercase flex items-center gap-1">
                        <span className="text-blue-400">{Math.round(score * 100)}%</span>
                        <span className="opacity-70">{t.home.match}</span>
                    </div>
                )}
            </div>

            <div className="p-5 relative">
                <div className="flex justify-between items-start mb-3 h-12">
                    <h3 className="text-sm font-bold text-zinc-100 line-clamp-2 leading-tight group-hover:text-blue-400 transition-colors tracking-tight">
                        {title}
                    </h3>
                </div>

                <div className="flex items-center text-[11px] text-zinc-500 mb-5 font-semibold tracking-wide uppercase">
                    <span className="truncate max-w-[150px]">{shopName}</span>
                </div>

                <div className="flex items-center justify-between mt-auto pt-4 border-t border-white/5">
                    <div className="flex flex-col">
                        <span className="text-sm font-bold text-zinc-100 tabular-nums">
                            {formatPrice(price)}
                        </span>
                    </div>
                    <a
                        href={boothUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-1.5 bg-zinc-100 hover:bg-white text-zinc-950 px-4 py-2 rounded-xl text-xs font-bold transition-all hover:scale-105 active:scale-95 shadow-lg shadow-white/5"
                    >
                        {t.home.viewOnBooth}
                        <ExternalLink size={14} strokeWidth={2.5} />
                    </a>
                </div>
            </div>
        </div>
    );
}
