import { useCallback } from 'react';
import apiService from 'services/api';

export function useApi() {
  const get = useCallback(apiService.get, []);
  const post = useCallback(apiService.post, []);

  return { get, post };
}