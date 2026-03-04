/**
 * Axios API client — configured for FastAPI backend.
 */
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ── Feed ──
export const fetchFeed = async ({ tag, cursor, limit = 15 }) => {
  const params = { limit };
  if (tag) params.tag = tag;
  if (cursor) params.cursor = cursor;

  const { data } = await apiClient.get('/feed', { params });
  return data;  // { items: [], next_cursor: string|null }
};

// ── Article Detail ──
export const fetchArticleDetail = async (articleId) => {
  const { data } = await apiClient.get(`/article/${articleId}`);
  return data;
};

// ── Tags ──
export const fetchTags = async () => {
  const { data } = await apiClient.get('/tags');
  return data;
};

// ── User Actions ──
export const saveArticle = async (articleId) => {
  const { data } = await apiClient.post(`/article/${articleId}/save`);
  return data;
};

export const dismissArticle = async (articleId) => {
  const { data } = await apiClient.post(`/article/${articleId}/dismiss`);
  return data;
};

export const undoDismiss = async (articleId) => {
  const { data } = await apiClient.post(`/article/${articleId}/undo`);
  return data;
};

export default apiClient;
