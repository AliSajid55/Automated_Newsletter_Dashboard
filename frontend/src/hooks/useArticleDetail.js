/**
 * useArticleDetail — fetches full article info when modal is opened.
 */
import { useQuery } from '@tanstack/react-query';
import { fetchArticleDetail } from '../api/client';

export function useArticleDetail(articleId, enabled = false) {
  return useQuery({
    queryKey: ['article', articleId],
    queryFn: () => fetchArticleDetail(articleId),
    enabled: !!articleId && enabled,
  });
}
