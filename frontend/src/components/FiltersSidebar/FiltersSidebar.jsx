import { motion, AnimatePresence } from 'framer-motion';
import { X, Tag } from 'lucide-react';
import { useTags } from '../../hooks/useTags';
import { TAG_COLORS } from '../../utils/constants';

export default function FiltersSidebar({ isOpen, onClose, activeTag, onTagSelect }) {
  const { data: tags, isLoading } = useTags();

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop (mobile) */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/40 z-30 lg:hidden"
            onClick={onClose}
          />

          {/* Sidebar */}
          <motion.aside
            initial={{ x: -300 }}
            animate={{ x: 0 }}
            exit={{ x: -300 }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
            className="fixed left-0 top-0 bottom-0 w-72 bg-gray-900 border-r border-gray-800 z-40 overflow-y-auto pt-20 pb-6"
          >
            {/* Header */}
            <div className="px-5 mb-6 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Tag className="w-4 h-4 text-primary-400" />
                <h2 className="text-sm font-semibold text-gray-200 uppercase tracking-wider">
                  Filter by Tag
                </h2>
              </div>
              <button
                onClick={onClose}
                className="p-1 rounded hover:bg-gray-800 text-gray-500 hover:text-white transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Clear Filter */}
            {activeTag && (
              <div className="px-5 mb-4">
                <button
                  onClick={() => onTagSelect(null)}
                  className="text-xs text-primary-400 hover:text-primary-300 underline"
                >
                  Clear filter
                </button>
              </div>
            )}

            {/* Tags List */}
            <div className="px-3">
              {isLoading ? (
                <div className="space-y-2 px-2">
                  {Array.from({ length: 8 }).map((_, i) => (
                    <div key={i} className="h-9 skeleton rounded-lg" />
                  ))}
                </div>
              ) : (
                <div className="space-y-1">
                  {tags?.map(({ tag, count }) => {
                    const isActive = activeTag === tag;
                    const colorClass = TAG_COLORS[tag] || 'bg-gray-700 text-gray-300';

                    return (
                      <button
                        key={tag}
                        onClick={() => onTagSelect(tag)}
                        className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm transition-all ${
                          isActive
                            ? 'bg-primary-600/20 text-primary-400 border border-primary-600/30'
                            : 'hover:bg-gray-800 text-gray-300'
                        }`}
                      >
                        <span className="font-medium">#{tag}</span>
                        <span className={`text-xs px-2 py-0.5 rounded-full ${
                          isActive ? 'bg-primary-600/30 text-primary-300' : 'bg-gray-800 text-gray-500'
                        }`}>
                          {count}
                        </span>
                      </button>
                    );
                  })}
                </div>
              )}
            </div>
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  );
}
