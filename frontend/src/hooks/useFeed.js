/**
 * useFeed — fetches paginated news feed with optional tag filter.
 * Uses useInfiniteQuery so CardStack can load more pages as user swipes.
 */
import { useInfiniteQuery } from '@tanstack/react-query';
import { fetchFeed } from '../api/client';

export function useFeed(activeTag = null) {
  return useInfiniteQuery({
    queryKey: ['feed', activeTag],
    queryFn: ({ pageParam }) => fetchFeed({ tag: activeTag, limit: 20, cursor: pageParam }),
    getNextPageParam: (lastPage) => lastPage.next_cursor ?? undefined,
    staleTime: 1000 * 60 * 2,  // 2 min
  });
}
