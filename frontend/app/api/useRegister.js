import { useMutation } from '@tanstack/react-query';
import { httpClient } from '../common/utils/client';

export function useRegister() {
  return useMutation({
    mutationFn: (data) =>
      httpClient({
        method: 'post',
        url: '/register',
        data,
      }),
  });
}
