import { useGetInterviewLogQuery } from '@/app/api/useInterviewClient';
import { useEffect, useState } from 'react';

export const GetInterviewLog = (interviewId) => {
  const [interviewLogList, setInterviewLogList] = useState([]);

  const {
    data: interviewLog,
    isError: interviewLogError,
    isLoading: interviewLogLoading,
  } = useGetInterviewLogQuery(interviewId);

  useEffect(() => {
    if (interviewLog) {
      setInterviewLogList(interviewLog.questions);
    }
  }, [interviewLog]);

  useEffect(() => {
    if (interviewLogError) {
      console.log(`인터뷰 기록 에러 발생: ${interviewLogError}`);
    }
  }, [interviewLogError]);

  return {
    interviewLogList,
  };
};
