import { useRef, useEffect } from 'react';
import { Clock, ExternalLink } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import TagChip from '../UI/TagChip';
import ImportanceBadge from '../UI/ImportanceBadge';
import SentimentDot from '../UI/SentimentDot';

export default function NewsCard({ article, onClick, stackIndex = 0 }) {
  const { title, source_name, published_at, ai, url } = article;
  const cardRef = useRef(null);

  // Track mouse/touch drag distance to apply swipe border colors
  // Uses pointer events directly — no state, no re-renders, no interference with drag
  useEffect(() => {
    const card = cardRef.current;
    if (!card || stackIndex !== 0) return;

    let startX = 0;
    let isDragging = false;

    const applyBorder = (dx) => {
      if (dx > 50) {
        card.style.borderColor = '#22c55e';
        card.style.boxShadow = '0 0 20px rgba(34,197,94,0.3)';
      } else if (dx < -50) {
        card.style.borderColor = '#ef4444';
        card.style.boxShadow = '0 0 20px rgba(239,68,68,0.3)';
      } else {
        card.style.borderColor = '#1f2937';
        card.style.boxShadow = '';
      }
    };

    const onDown = (e) => {
      isDragging = true;
      startX = e.type === 'touchstart' ? e.touches[0].clientX : e.clientX;
    };

    const onMove = (e) => {
      if (!isDragging) return;
      const currentX = e.type === 'touchmove' ? e.touches[0].clientX : e.clientX;
      applyBorder(currentX - startX);
    };

    const onUp = () => {
      if (!isDragging) return;
      isDragging = false;
      // Reset border after a short delay (card may fly away or snap back)
      setTimeout(() => {
        if (card) {
          card.style.borderColor = '#1f2937';
          card.style.boxShadow = '';
        }
      }, 100);
    };

    card.addEventListener('mousedown', onDown);
    card.addEventListener('touchstart', onDown, { passive: true });
    window.addEventListener('mousemove', onMove);
    window.addEventListener('touchmove', onMove, { passive: true });
    window.addEventListener('mouseup', onUp);
    window.addEventListener('touchend', onUp);

    return () => {
      card.removeEventListener('mousedown', onDown);
      card.removeEventListener('touchstart', onDown);
      window.removeEventListener('mousemove', onMove);
      window.removeEventListener('touchmove', onMove);
      window.removeEventListener('mouseup', onUp);
      window.removeEventListener('touchend', onUp);
    };
  }, [stackIndex]);

  // Stack effect — cards behind are slightly smaller and offset
  const stackStyle = {
    transform: `scale(${1 - stackIndex * 0.03}) translateY(${stackIndex * 8}px)`,
    zIndex: 10 - stackIndex,
    opacity: stackIndex > 2 ? 0 : 1,
  };

  const timeAgo = published_at
    ? formatDistanceToNow(new Date(published_at), { addSuffix: true })
    : '';

  return (
    <div
      ref={cardRef}
      className="relative w-full bg-gray-900 rounded-2xl border-2 border-gray-800 shadow-2xl overflow-hidden cursor-pointer select-none"
      style={stackStyle}
      onClick={onClick}
    >
      {/* ── Top Section: Source + Time ── */}
      <div className="px-5 pt-5 pb-2 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 bg-primary-600/20 rounded-full flex items-center justify-center text-xs font-bold text-primary-400">
            {source_name?.charAt(0) || '?'}
          </div>
          <span className="text-sm font-medium text-gray-300">{source_name}</span>
        </div>
        <div className="flex items-center gap-1 text-gray-500 text-xs">
          <Clock className="w-3 h-3" />
          <span>{timeAgo}</span>
        </div>
      </div>

      {/* ── Title ── */}
      <div className="px-5 py-3">
        <h2 className="text-lg font-semibold text-white leading-snug line-clamp-3">
          {title}
        </h2>
      </div>

      {/* ── AI Summary Preview ── */}
      {ai?.summary_short && (
        <div className="px-5 pb-3">
          <p className="text-sm text-gray-400 leading-relaxed line-clamp-2">
            {ai.summary_short}
          </p>
        </div>
      )}

      {/* ── Tags ── */}
      {ai?.tags && ai.tags.length > 0 && (
        <div className="px-5 pb-3 flex flex-wrap gap-1.5">
          {ai.tags.slice(0, 4).map((tag) => (
            <TagChip key={tag} tag={tag} />
          ))}
        </div>
      )}

      {/* ── Footer: Importance + Sentiment ── */}
      <div className="px-5 py-3 border-t border-gray-800/50 flex items-center justify-between">
        <div className="flex items-center gap-2">
          {ai?.importance_score && (
            <ImportanceBadge score={ai.importance_score} />
          )}
          {ai?.sentiment && (
            <SentimentDot sentiment={ai.sentiment} />
          )}
        </div>
        <a
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          className="p-1.5 rounded-lg hover:bg-gray-800 text-gray-500 hover:text-primary-400 transition-colors"
          onClick={(e) => e.stopPropagation()}
          title="Open original"
        >
          <ExternalLink className="w-4 h-4" />
        </a>
      </div>
    </div>
  );
}
