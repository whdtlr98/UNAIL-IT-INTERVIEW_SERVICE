import { useQuery, useMutation } from '@tanstack/react-query';
import { httpClient } from '../common/utils/client';

export function useGetQuestionMutation() {
  return useMutation({
    mutationFn: ({ resume, user_job, user_id }) => {
      const formData = new FormData();
      formData.append('resume', resume);
      formData.append('user_job', user_job);
      formData.append('user_id', user_id);

      return httpClient({
        method: 'post',
        url: '/generate_question',
        data: formData,
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
    },
  });
}

export function usePostEvaluationMutation() {
  return useMutation({
    mutationFn: (data) =>
      httpClient({
        method: 'post',
        url: '/evaluate_answers',
        data: data,
      }),
  });
}

export function useGetInterviewLogQuery(interview_id) {
  return useQuery({
    queryKey: [`/interviews/${interview_id}/questions`],
    queryFn: () =>
      httpClient({
        method: 'get',
        url: `/interviews/${interview_id}/questions`,
      }),
    enabled: !!interview_id,
  });
}

export function useGetInterviewReport(interview_id) {
  return useQuery({
    queryKey: [`/interviews/${interview_id}/report`],
    queryFn: () =>
      httpClient({
        method: 'get',
        url: `/interviews/${interview_id}/report`,
      }),
    enabled: !!interview_id,
  });
}
