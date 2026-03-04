import Header from './Header';

export default function Layout({ children, onToggleSidebar, activeTag }) {
  return (
    <div className="min-h-screen bg-gray-950 flex flex-col">
      <Header onToggleSidebar={onToggleSidebar} activeTag={activeTag} />
      <div className="flex-1 overflow-hidden">
        {children}
      </div>
    </div>
  );
}
