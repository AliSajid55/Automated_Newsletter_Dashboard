/**
 * useTags — fetches all tags with counts for the filter sidebar.
 */
import { useQuery } from '@tanstack/react-query';
import { fetchTags } from '../api/client';

export function useTags() {
  return useQuery({
    queryKey: ['tags'],
    queryFn: fetchTags,
    staleTime: 1000 * 60 * 10, // 10 min — tags don't change often
  });
}
