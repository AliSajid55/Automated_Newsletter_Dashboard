export default function SentimentDot({ sentiment }) {
  const config = {
    Positive: { color: 'bg-green-400', label: 'Positive' },
    Negative: { color: 'bg-red-400', label: 'Negative' },
    Neutral: { color: 'bg-gray-400', label: 'Neutral' },
  };

  const { color, label } = config[sentiment] || config.Neutral;

  return (
    <span className="inline-flex items-center gap-1.5 text-[11px] text-gray-400">
      <span className={`w-2 h-2 rounded-full ${color}`} />
      {label}
    </span>
  );
}
