import { useMutation } from '@tanstack/react-query';
import { httpClient } from '../common/utils/client';

export function useRefresh() {
  return useMutation({
    mutationFn: ({ refresh_token }) =>
      httpClient({
        method: 'post',
        url: '/refresh',
        params: { refresh_token },
      }),
  });
}
