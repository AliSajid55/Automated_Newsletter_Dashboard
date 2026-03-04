import { TAG_COLORS } from '../../utils/constants';

export default function TagChip({ tag, size = 'sm' }) {
  const colorClass = TAG_COLORS[tag] || 'bg-gray-700/50 text-gray-300 border-gray-600';

  const sizeClass = size === 'sm'
    ? 'px-2 py-0.5 text-[11px]'
    : 'px-3 py-1 text-xs';

  return (
    <span
      className={`inline-flex items-center rounded-full font-medium border ${colorClass} ${sizeClass}`}
    >
      #{tag}
    </span>
  );
}
