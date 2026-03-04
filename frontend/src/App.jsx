import { useState } from 'react';
import Layout from './components/Layout/Layout';
import CardStack from './components/CardStack/CardStack';
import SummaryModal from './components/SummaryModal/SummaryModal';
import FiltersSidebar from './components/FiltersSidebar/FiltersSidebar';

function App() {
  const [selectedArticle, setSelectedArticle] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [activeTag, setActiveTag] = useState(null);

  const handleCardClick = (article) => {
    setSelectedArticle(article);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedArticle(null);
  };

  const handleTagSelect = (tag) => {
    setActiveTag(tag === activeTag ? null : tag);
    setIsSidebarOpen(false);
  };

  return (
    <Layout
      onToggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)}
      activeTag={activeTag}
    >
      <div className="flex h-full">
        <FiltersSidebar
          isOpen={isSidebarOpen}
          onClose={() => setIsSidebarOpen(false)}
          activeTag={activeTag}
          onTagSelect={handleTagSelect}
        />

        <main className="flex-1 flex items-center justify-center p-4">
          <CardStack
            activeTag={activeTag}
            onCardClick={handleCardClick}
          />
        </main>
      </div>

      <SummaryModal
        article={selectedArticle}
        isOpen={isModalOpen}
        onClose={handleCloseModal}
      />
    </Layout>
  );
}

export default App;
