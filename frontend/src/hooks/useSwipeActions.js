/**
 * useSwipeActions — save, dismiss, undo mutations.
 */
import { useMutation, useQueryClient } from '@tanstack/react-query';
import {
  saveArticle as saveArticleApi,
  dismissArticle as dismissArticleApi,
  undoDismiss as undoDismissApi,
} from '../api/client';

export function useSwipeActions() {
  const queryClient = useQueryClient();

  const saveMutation = useMutation({
    mutationFn: saveArticleApi,
    // Don't invalidate feed on save — avoids resetting the card stack
  });

  const dismissMutation = useMutation({
    mutationFn: dismissArticleApi,
    // Don't invalidate feed on dismiss — avoids resetting the card stack
  });

  const undoMutation = useMutation({
    mutationFn: undoDismissApi,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['feed'] });
    },
  });

  return {
    saveArticle: (id) => saveMutation.mutate(id),
    dismissArticle: (id) => dismissMutation.mutate(id),
    undoDismiss: (id) => undoMutation.mutate(id),
  };
}
