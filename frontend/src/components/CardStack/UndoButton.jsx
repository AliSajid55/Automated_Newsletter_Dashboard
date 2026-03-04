import { motion } from 'framer-motion';
import { Undo2 } from 'lucide-react';

export default function UndoButton({ onUndo }) {
  return (
    <motion.button
      initial={{ opacity: 0, y: 20, scale: 0.8 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: 20, scale: 0.8 }}
      transition={{ type: 'spring', stiffness: 300, damping: 20 }}
      onClick={onUndo}
      className="fixed bottom-8 left-1/2 -translate-x-1/2 z-50 flex items-center gap-2 px-5 py-2.5 bg-gray-800 hover:bg-gray-700 border border-gray-700 text-white rounded-full shadow-lg transition-colors"
    >
      <Undo2 className="w-4 h-4" />
      <span className="text-sm font-medium">Undo</span>
    </motion.button>
  );
}
