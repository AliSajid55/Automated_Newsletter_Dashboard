import { useState, useRef, useMemo, useEffect } from 'react';
import TinderCard from 'react-tinder-card';
import { AnimatePresence } from 'framer-motion';
import NewsCard from './NewsCard';
import UndoButton from './UndoButton';
import SkeletonCard from '../UI/SkeletonCard';
import { useFeed } from '../../hooks/useFeed';
import { useSwipeActions } from '../../hooks/useSwipeActions';

export default function CardStack({ activeTag, onCardClick }) {
  const {
    data,
    isLoading,
    isError,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useFeed(activeTag);
  const { saveArticle, dismissArticle, undoDismiss } = useSwipeActions();

  const [lastDismissed, setLastDismissed] = useState(null);
  const [showUndo, setShowUndo] = useState(false);
  const [currentIndex, setCurrentIndex] = useState(0);
  const undoTimerRef = useRef(null);

  // Flatten all pages into a single articles array
  const articles = useMemo(() => {
    if (!data) return [];
    return data.pages.flatMap((page) => page.items);
  }, [data]);

  // When we're 5 cards from the end, prefetch the next page
  useEffect(() => {
    if (articles.length > 0 && currentIndex >= articles.length - 5 && hasNextPage && !isFetchingNextPage) {
      fetchNextPage();
    }
  }, [currentIndex, articles.length, hasNextPage, isFetchingNextPage, fetchNextPage]);

  // Cards to display (reversed for stack order)
  const visibleCards = useMemo(() => {
    if (!articles) return [];
    return articles.slice(currentIndex, currentIndex + 5);
  }, [articles, currentIndex]);

  const handleSwipe = (direction, article) => {
    if (direction === 'right') {
      saveArticle(article.id);
    } else if (direction === 'left') {
      dismissArticle(article.id);
      setLastDismissed(article);
      setShowUndo(true);

      // Auto-hide undo after 2 seconds
      clearTimeout(undoTimerRef.current);
      undoTimerRef.current = setTimeout(() => {
        setShowUndo(false);
        setLastDismissed(null);
      }, 2000);
    }

    setCurrentIndex((prev) => prev + 1);
  };

  const handleUndo = () => {
    if (lastDismissed) {
      undoDismiss(lastDismissed.id);
      setCurrentIndex((prev) => Math.max(0, prev - 1));
      setShowUndo(false);
      setLastDismissed(null);
      clearTimeout(undoTimerRef.current);
    }
  };

  const handleCardLeft = () => {
    // No-op: index already incremented in handleSwipe
  };

  // ── Loading State ──
  if (isLoading) {
    return (
      <div className="relative w-full max-w-sm mx-auto h-[520px]">
        <SkeletonCard />
      </div>
    );
  }

  // ── Error State ──
  if (isError) {
    return (
      <div className="text-center text-gray-400 py-20">
        <p className="text-lg font-medium text-red-400">Failed to load news feed</p>
        <p className="text-sm mt-1">Check your connection and try again.</p>
      </div>
    );
  }

  // ── Loading next page (buffer exhausted but more coming) ──
  if (isFetchingNextPage && visibleCards.length === 0) {
    return (
      <div className="relative w-full max-w-sm mx-auto h-[520px]">
        <SkeletonCard />
      </div>
    );
  }

  // ── Empty State ──
  if (!articles || articles.length === 0 || (currentIndex >= articles.length && !hasNextPage)) {
    return (
      <div className="text-center text-gray-400 py-20">
        <p className="text-xl font-semibold text-gray-300">You're all caught up! 🎉</p>
        <p className="text-sm mt-2">No more news to swipe. Check back later.</p>
      </div>
    );
  }

  return (
    <div className="relative w-full max-w-sm mx-auto h-[520px]">
      {/* Card Stack — rendered in reverse so the top card is last in the DOM (captures mouse/touch) */}
      <div className="relative w-full h-full">
        {[...visibleCards].reverse().map((article, reverseIndex) => {
          const stackIndex = visibleCards.length - 1 - reverseIndex;
          return (
            <TinderCard
              key={article.id}
              onSwipe={(dir) => handleSwipe(dir, article)}
              onCardLeftScreen={handleCardLeft}
              preventSwipe={['up', 'down']}
              className="absolute w-full"
            >
              <NewsCard
                article={article}
                onClick={() => onCardClick(article)}
                stackIndex={stackIndex}
              />
            </TinderCard>
          );
        })}
      </div>

      {/* Swipe Hints */}
      <div className="flex justify-between mt-4 px-4 text-xs text-gray-500">
        <span>← Dismiss</span>
        <span>Tap for summary</span>
        <span>Save →</span>
      </div>

      {/* Undo Button */}
      <AnimatePresence>
        {showUndo && (
          <UndoButton onUndo={handleUndo} />
        )}
      </AnimatePresence>
    </div>
  );
}
