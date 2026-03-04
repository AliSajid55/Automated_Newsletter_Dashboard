import { Star, Zap, AlertTriangle } from 'lucide-react';

export default function ImportanceBadge({ score }) {
  if (score >= 8) {
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 text-[11px] font-bold bg-amber-500/20 text-amber-400 border border-amber-500/30 rounded-full">
        <Zap className="w-3 h-3" />
        Must Read
      </span>
    );
  }

  if (score >= 6) {
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 text-[11px] font-medium bg-blue-500/20 text-blue-400 border border-blue-500/30 rounded-full">
        <Star className="w-3 h-3" />
        Important
      </span>
    );
  }

  return (
    <span className="inline-flex items-center gap-1 px-2 py-0.5 text-[11px] font-medium bg-gray-700/50 text-gray-400 border border-gray-600/50 rounded-full">
      Score: {score}
    </span>
  );
}
