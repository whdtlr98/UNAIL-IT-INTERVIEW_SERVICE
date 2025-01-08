import { useQuery } from '@tanstack/react-query';
import { httpClient } from '../common/utils/client';

export function useGetInterviewHistory(user_id) {
  return useQuery({
    queryKey: [`interview/${user_id}`],
    queryFn: () =>
      httpClient({
        method: 'get',
        url: `/interview/${user_id}`,
      }),
    enabled: !!user_id,
  });
}
