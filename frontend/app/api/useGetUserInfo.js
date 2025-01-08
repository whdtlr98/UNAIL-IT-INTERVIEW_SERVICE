import { useQuery } from '@tanstack/react-query';
import { httpClient } from '../common/utils/client';

export function useGetUserInfo(id) {
  return useQuery({
    queryKey: [`users/${id}`],
    queryFn: () =>
      httpClient({
        method: 'get',
        url: `/users/${id}`,
      }),
    enabled: !!id,
  });
}
