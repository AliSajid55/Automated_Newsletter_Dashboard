import { motion, AnimatePresence } from 'framer-motion';
import {
  X,
  ExternalLink,
  Bookmark,
  Share2,
  Clock,
  ChevronRight,
} from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import TagChip from '../UI/TagChip';
import ImportanceBadge from '../UI/ImportanceBadge';
import SentimentDot from '../UI/SentimentDot';
import { useArticleDetail } from '../../hooks/useArticleDetail';
import { useSwipeActions } from '../../hooks/useSwipeActions';

export default function SummaryModal({ article, isOpen, onClose }) {
  const { data: detail, isLoading } = useArticleDetail(article?.id, isOpen);
  const { saveArticle } = useSwipeActions();

  if (!isOpen) return null;

  const displayData = detail || article;

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: displayData.title,
          url: displayData.url,
        });
      } catch (err) {
        // User cancelled sharing
      }
    } else {
      navigator.clipboard.writeText(displayData.url);
    }
  };

  const handleSave = () => {
    saveArticle(displayData.id);
  };

  const timeAgo = displayData?.published_at
    ? formatDistanceToNow(new Date(displayData.published_at), { addSuffix: true })
    : '';

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50"
            onClick={onClose}
          />

          {/* Bottom Sheet */}
          <motion.div
            initial={{ y: '100%' }}
            animate={{ y: 0 }}
            exit={{ y: '100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
            className="fixed bottom-0 left-0 right-0 z-50 max-h-[85vh] bg-gray-900 rounded-t-3xl overflow-hidden shadow-2xl"
          >
            {/* Drag Handle */}
            <div className="flex justify-center pt-3 pb-1">
              <div className="w-10 h-1 bg-gray-700 rounded-full" />
            </div>

            {/* Content */}
            <div className="overflow-y-auto max-h-[80vh] px-6 pb-8">
              {/* Close Button */}
              <div className="flex justify-end mb-2">
                <button
                  onClick={onClose}
                  className="p-1.5 rounded-lg hover:bg-gray-800 text-gray-400 hover:text-white transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {isLoading ? (
                <div className="space-y-4 animate-pulse">
                  <div className="h-6 bg-gray-800 rounded w-3/4" />
                  <div className="h-4 bg-gray-800 rounded w-1/2" />
                  <div className="h-20 bg-gray-800 rounded" />
                </div>
              ) : (
                <>
                  {/* Source & Time */}
                  <div className="flex items-center gap-2 mb-3 text-sm text-gray-400">
                    <span className="font-medium text-primary-400">{displayData?.source_name}</span>
                    {timeAgo && (
                      <>
                        <span>•</span>
                        <Clock className="w-3 h-3" />
                        <span>{timeAgo}</span>
                      </>
                    )}
                  </div>

                  {/* Title */}
                  <h2 className="text-xl font-bold text-white leading-snug mb-4">
                    {displayData?.title}
                  </h2>

                  {/* Tags */}
                  {displayData?.ai?.tags && (
                    <div className="flex flex-wrap gap-1.5 mb-4">
                      {displayData.ai.tags.map((tag) => (
                        <TagChip key={tag} tag={tag} />
                      ))}
                    </div>
                  )}

                  {/* Importance & Sentiment */}
                  <div className="flex items-center gap-3 mb-5">
                    {displayData?.ai?.importance_score && (
                      <ImportanceBadge score={displayData.ai.importance_score} />
                    )}
                    {displayData?.ai?.sentiment && (
                      <SentimentDot sentiment={displayData.ai.sentiment} />
                    )}
                  </div>

                  {/* Summary */}
                  {displayData?.ai?.summary_short && (
                    <div className="mb-5">
                      <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-2">
                        Summary
                      </h3>
                      <p className="text-gray-300 leading-relaxed">
                        {displayData.ai.summary_short}
                      </p>
                    </div>
                  )}

                  {/* Bullet Points */}
                  {displayData?.ai?.summary_bullets && displayData.ai.summary_bullets.length > 0 && (
                    <div className="mb-6">
                      <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-3">
                        Key Highlights
                      </h3>
                      <ul className="space-y-2">
                        {displayData.ai.summary_bullets.map((bullet, idx) => (
                          <li key={idx} className="flex items-start gap-2 text-gray-300">
                            <ChevronRight className="w-4 h-4 text-primary-400 mt-0.5 flex-shrink-0" />
                            <span className="text-sm leading-relaxed">{bullet}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Action Buttons */}
                  <div className="flex gap-3 pt-4 border-t border-gray-800">
                    <a
                      href={displayData?.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-primary-600 hover:bg-primary-700 text-white rounded-xl font-medium transition-colors"
                    >
                      <ExternalLink className="w-4 h-4" />
                      Open Original
                    </a>
                    <button
                      onClick={handleSave}
                      className="p-3 bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded-xl text-gray-300 hover:text-white transition-colors"
                      title="Save for later"
                    >
                      <Bookmark className="w-5 h-5" />
                    </button>
                    <button
                      onClick={handleShare}
                      className="p-3 bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded-xl text-gray-300 hover:text-white transition-colors"
                      title="Share"
                    >
                      <Share2 className="w-5 h-5" />
                    </button>
                  </div>
                </>
              )}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
