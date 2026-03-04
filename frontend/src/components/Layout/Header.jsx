import { Newspaper, Filter, BookmarkIcon } from 'lucide-react';

export default function Header({ onToggleSidebar, activeTag }) {
  return (
    <header className="sticky top-0 z-40 bg-gray-950/80 backdrop-blur-xl border-b border-gray-800">
      <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
        {/* Logo & Title */}
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 bg-primary-600 rounded-lg flex items-center justify-center">
            <Newspaper className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-white leading-tight">
              CTO's Morning Brief
            </h1>
            <p className="text-xs text-gray-400">AI-powered tech digest</p>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2">
          {activeTag && (
            <span className="px-2.5 py-1 text-xs font-medium bg-primary-600/20 text-primary-400 rounded-full border border-primary-600/30">
              #{activeTag}
            </span>
          )}
          <button
            onClick={onToggleSidebar}
            className="p-2 rounded-lg hover:bg-gray-800 transition-colors text-gray-400 hover:text-white"
            title="Filters"
          >
            <Filter className="w-5 h-5" />
          </button>
        </div>
      </div>
    </header>
  );
}
