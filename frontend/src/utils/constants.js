/**
 * Constants — tag colors, taxonomy, sentiment config.
 */

// Tag color classes for Tailwind (background + text + border)
export const TAG_COLORS = {
  // Security
  CyberSecurity: 'bg-red-500/15 text-red-400 border-red-500/30',
  Privacy: 'bg-red-500/15 text-red-300 border-red-500/30',
  Vulnerability: 'bg-red-600/15 text-red-400 border-red-600/30',

  // Dev
  WebDev: 'bg-blue-500/15 text-blue-400 border-blue-500/30',
  MobileDev: 'bg-blue-500/15 text-blue-300 border-blue-500/30',
  DevOps: 'bg-cyan-500/15 text-cyan-400 border-cyan-500/30',
  Cloud: 'bg-sky-500/15 text-sky-400 border-sky-500/30',

  // Data / AI
  AI: 'bg-purple-500/15 text-purple-400 border-purple-500/30',
  ML: 'bg-violet-500/15 text-violet-400 border-violet-500/30',
  Data: 'bg-indigo-500/15 text-indigo-400 border-indigo-500/30',

  // Business
  FinTech: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30',
  Startups: 'bg-orange-500/15 text-orange-400 border-orange-500/30',
  BigTech: 'bg-amber-500/15 text-amber-400 border-amber-500/30',

  // Infrastructure
  Databases: 'bg-teal-500/15 text-teal-400 border-teal-500/30',
  Networking: 'bg-lime-500/15 text-lime-400 border-lime-500/30',
  Hardware: 'bg-stone-500/15 text-stone-400 border-stone-500/30',

  // Misc
  GeneralTech: 'bg-gray-500/15 text-gray-400 border-gray-500/30',
  Others: 'bg-gray-600/15 text-gray-400 border-gray-600/30',
};

// Sentiment colors
export const SENTIMENT_CONFIG = {
  Positive: { color: 'text-green-400', bg: 'bg-green-400', label: 'Positive' },
  Negative: { color: 'text-red-400', bg: 'bg-red-400', label: 'Negative' },
  Neutral: { color: 'text-gray-400', bg: 'bg-gray-400', label: 'Neutral' },
};

// All allowed tags (matches backend taxonomy)
export const ALL_TAGS = [
  'CyberSecurity', 'Privacy', 'Vulnerability',
  'WebDev', 'MobileDev', 'DevOps', 'Cloud',
  'AI', 'ML', 'Data',
  'FinTech', 'Startups', 'BigTech',
  'Databases', 'Networking', 'Hardware',
  'GeneralTech', 'Others',
];
