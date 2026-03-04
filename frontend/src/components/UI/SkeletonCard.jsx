/**
 * Skeleton card — shown while news cards are loading.
 * Gray placeholder structure for "premium" feel.
 */
export default function SkeletonCard() {
  return (
    <div className="w-full bg-gray-900 rounded-2xl border border-gray-800 overflow-hidden">
      {/* Top bar */}
      <div className="px-5 pt-5 pb-2 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 skeleton rounded-full" />
          <div className="w-24 h-3 skeleton rounded" />
        </div>
        <div className="w-14 h-3 skeleton rounded" />
      </div>

      {/* Title skeleton */}
      <div className="px-5 py-3 space-y-2">
        <div className="w-full h-5 skeleton rounded" />
        <div className="w-4/5 h-5 skeleton rounded" />
        <div className="w-2/3 h-5 skeleton rounded" />
      </div>

      {/* Summary skeleton */}
      <div className="px-5 pb-3 space-y-2">
        <div className="w-full h-3 skeleton rounded" />
        <div className="w-3/4 h-3 skeleton rounded" />
      </div>

      {/* Tags skeleton */}
      <div className="px-5 pb-3 flex gap-1.5">
        <div className="w-16 h-5 skeleton rounded-full" />
        <div className="w-20 h-5 skeleton rounded-full" />
        <div className="w-14 h-5 skeleton rounded-full" />
      </div>

      {/* Footer skeleton */}
      <div className="px-5 py-3 border-t border-gray-800/50 flex items-center justify-between">
        <div className="w-20 h-5 skeleton rounded-full" />
        <div className="w-8 h-8 skeleton rounded-lg" />
      </div>
    </div>
  );
}
